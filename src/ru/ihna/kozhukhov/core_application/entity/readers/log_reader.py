from ipaddress import ip_address

from .raw_sql_query_reader import RawSqlQueryReader
from .query_builders.query_filters import StringQueryFilter
from .model_emulators import ModelEmulator, time_from_db, prepare_time
from ..providers.model_providers.log_provider import LogProvider


class LogReader(RawSqlQueryReader):
    """
    Retrieves the log information from the database and saves it to the hard disk drive
    """

    _entity_provider = LogProvider()

    _lookup_table_name = "core_application_log"

    _query_debug = False

    _count_join = False

    def initialize_query_builder(self):
        self.items_builder\
            .add_select_expression("core_application_log.id")\
            .add_select_expression("core_application_log.request_date")\
            .add_select_expression("core_application_log.log_address")\
            .add_select_expression("core_application_log.request_method")\
            .add_select_expression("core_application_log.operation_description")\
            .add_select_expression("core_application_log.request_body")\
            .add_select_expression("core_application_log.input_data")\
            .add_select_expression("core_application_log.ip_address")\
            .add_select_expression("core_application_log.geolocation")\
            .add_select_expression("core_application_log.response_status")\
            .add_select_expression("core_application_log.response_body")\
            .add_select_expression("core_application_log.output_data")\
            .add_select_expression("core_application_user.id")\
            .add_select_expression("core_application_user.login")\
            .add_select_expression("core_application_user.name")\
            .add_select_expression("core_application_user.surname")\
            .add_data_source("core_application_log")\
            .add_order_term("core_application_log.request_date", direction=self.items_builder.DESC)
        self.items_builder.data_source\
            .add_join(self.items_builder.JoinType.LEFT, "core_application_user",
                      "ON (core_application_user.id=core_application_log.user_id)")

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source("core_application_log")
        self._count_join = False

    def apply_request_date_from_filter(self, time):
        """
        Selects logs that were made later than a given time

        :param time: the time from
        :return: nothing
        """
        for builder in [self.items_builder, self.count_builder]:
            builder.main_filter &= StringQueryFilter(
                "core_application_log.request_date >= %s",
                prepare_time(time)
            )

    def apply_request_date_to_filter(self, time):
        """
        Selects logs that were made earlier than a given time

        :param time: the time to
        :return: nothing
        """
        for builder in [self.items_builder, self.count_builder]:
            builder.main_filter &= StringQueryFilter(
                "core_application_log.request_date <= %s",
                prepare_time(time)
            )

    def apply_ip_address_filter(self, ip):
        """
        Selects only logs received from a certain remote IP address.

        :param ip: the IP address from which logs shall be received.
        :return: nothing
        """
        ip = str(ip_address(ip))
        for builder in [self.items_builder, self.count_builder]:
            builder.main_filter &= StringQueryFilter("core_application_log.ip_address = %s", ip)

    def apply_user_filter(self, user):
        """
        Select only logs from a certain authorized user

        :param user: the authorized user
        :return: nothing
        """
        for builder in [self.items_builder, self.count_builder]:
            builder.main_filter &= StringQueryFilter("core_application_log.user_id=%s", user.id)

    def apply_is_anonymous_filter(self, is_anonymous):
        """
        Selects only logs from anonymous users

        :param is_anonymous: True if you need to select logs from anonymous users only, False otherwise
        :return: nothing
        """
        if is_anonymous:
            for builder in [self.items_builder, self.count_builder]:
                builder.main_filter &= StringQueryFilter("core_application_log.user_id IS NULL")

    def apply_is_success_filter(self, is_success):
        """
        Selects only logs related to successive responses

        :param is_success: True if you need to apply this filter, False if you need to discard this filter
        :return: nothing
        """
        if is_success:
            for builder in [self.items_builder, self.count_builder]:
                builder.main_filter &= StringQueryFilter("core_application_log.response_status >= 200") & \
                    StringQueryFilter("core_application_log.response_status < 299")

    def apply_is_fail_filter(self, is_fail):
        """
        Selects only logs related to failed responses

        :param is_fail: True if you need to apply this filter, False if you need to discard this filter
        :return: nothing
        """
        if is_fail:
            for builder in [self.items_builder, self.count_builder]:
                builder.main_filter &= StringQueryFilter("core_application_log.response_status >= 400") & \
                    StringQueryFilter("core_application_log.response_status < 599")

    def create_external_object(self, log_id, request_date, log_address, request_method, operation_description,
                               request_body, input_data, ip_address, geolocation, response_status, response_body,
                               output_data,
                               user_id, user_login, user_name, user_surname):
        if user_id is None:
            user = None
        else:
            user = ModelEmulator(id=user_id, login=user_login, name=user_name, surname=user_surname)
        return ModelEmulator(
            id=log_id,
            request_date=time_from_db(request_date),
            log_address=log_address,
            request_method=request_method,
            operation_description=operation_description,
            request_body=request_body,
            input_data=input_data,
            user=user,
            ip_address=ip_address,
            geolocation=geolocation,
            response_status=response_status,
            response_body=response_body,
            output_data=output_data
        )
