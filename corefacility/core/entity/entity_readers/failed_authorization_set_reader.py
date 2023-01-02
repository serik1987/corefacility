from datetime import datetime
from ipaddress import ip_address

from .raw_sql_query_reader import RawSqlQueryReader
from ..entity_providers.model_providers.failed_authorization_provider import FailedAuthorizationProvider
from .model_emulators import ModelEmulator, time_from_db, prepare_time
from .query_builders.query_filters import StringQueryFilter


class FailedAuthorizationSetReader(RawSqlQueryReader):
    """
    Reads the data from the database and moves them to the FailedAuthorizationSet entity sets
    """

    _query_debug = False

    _entity_provider = FailedAuthorizationProvider()
    """
    The instance of the entity provider. When the EntityReader finds an information about
    the entity from the external source that satisfies filter conditions, it calls the
    wrap_entity method of the _entity_provider given here
    """

    def initialize_query_builder(self):
        """
        This function shall call certain methods for the query builder to make
        it to generate proper queries given that no external filters applied

        :return: nothing
        """
        self.count_builder.add_select_expression(self.count_builder.select_total_count())
        self.items_builder.add_order_term('auth_time', self.items_builder.DESC)
        for builder in (self.items_builder, self.count_builder):
            builder.add_data_source('core_failedauthorizations')

    def apply_expiry_term_filter(self, expiry_term):
        """
        Applies the expiry term filter
        :param expiry_term: expiry term to filter
        :return: nothing
        """
        min_time = prepare_time(datetime.now() - expiry_term)
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter('auth_time >= %s', min_time)

    def apply_ip_filter(self, ip):
        """
        Filters attempts made from a given IP address
        :param ip: the IP address itself
        :return: nothing
        """
        ip = str(ip_address(ip))
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter('ip = %s', ip)

    def apply_user_filter(self, user):
        """
        Filters attempts made on behalf of a given user
        :param user: the user itself
        :return: nothing
        """
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter('user_id = %s', user.id)

    def create_external_object(self, id, auth_time, ip, user_id):
        """
        Transforms the query result row into any external object that is able to read by the entity reader
        """
        return ModelEmulator(
            id=id,
            auth_time=time_from_db(auth_time),
            ip=ip,
            user=ModelEmulator(
                id=user_id
            )
        )
