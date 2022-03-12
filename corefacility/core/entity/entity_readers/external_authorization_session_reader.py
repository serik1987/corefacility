from uuid import UUID

from .query_builders.query_filters import StringQueryFilter
from .raw_sql_query_reader import RawSqlQueryReader
from .model_emulators import ModelEmulator, time_from_db
from ..entity_providers.model_providers.external_authorization_session_provider import \
    ExternalAuthorizationSessionProvider


class ExternalAuthorizationSessionReader(RawSqlQueryReader):
    """
    Finds an appropriate external authorization session from the database and sends it to the
    ExternalAuthorizationSessionProvider
    """

    _entity_provider = ExternalAuthorizationSessionProvider()

    _query_debug = False
    """ Set this field to True if debugging is needed """

    def initialize_query_builder(self):
        """
        Creates initial SQL queries which will be executed during iteration or item counts
        where no additional filters were applied

        :return: nothing
        """
        self.items_builder\
            .add_select_expression("core_externalauthorizationsession.id")\
            .add_select_expression("core_externalauthorizationsession.session_key")\
            .add_select_expression("core_externalauthorizationsession.session_key_expiry_date") \
            .add_select_expression("core_module.uuid") \
            .add_select_expression("core_module.alias")\
            .add_select_expression("core_module.name")\
            .add_select_expression("core_module.html_code")\
            .add_select_expression("core_module.app_class")\
            .add_select_expression("core_module.user_settings")\
            .add_select_expression("core_module.is_application")\
            .add_select_expression("core_module.is_enabled") \
            .add_order_term("core_externalauthorizationsession.id")

        self.count_builder.add_select_expression(self.count_builder.select_total_count())

        for builder in (self.items_builder, self.count_builder):
            builder.add_data_source("core_externalauthorizationsession")
            builder.data_source.add_join(builder.JoinType.INNER, "core_module",
                                         "ON (core_module.uuid=authorization_module_id)")

    def apply_authorization_module_filter(self, module):
        """
        Selects only those external authorization sessions that belong to a given module

        :param module: the module which they shall belong to
        :return: nothing
        """
        module_uuid = str(module.uuid).replace("-", "")
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("core_module.uuid=%s", module_uuid)

    def create_external_object(self, session_id, session_key, session_key_expiry_date,
                               module_uuid, module_alias, module_name, module_html_code, module_app_class,
                               module_user_settings, module_is_application, module_is_enabled):
        if isinstance(module_uuid, str):
            module_uuid = UUID(module_uuid)
        return ModelEmulator(
            id=session_id,
            session_key=session_key,
            session_key_expiry_date=time_from_db(session_key_expiry_date),
            authorization_module=ModelEmulator(
                id=None,
                uuid=module_uuid,
                alias=module_alias,
                name=module_name,
                html_code=module_html_code,
                app_class=module_app_class,
                user_settings=module_user_settings,
                is_application=module_is_application,
                is_enabled=module_is_enabled
            )
        )
