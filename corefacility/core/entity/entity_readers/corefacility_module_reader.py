from uuid import UUID

from .raw_sql_query_reader import RawSqlQueryReader
from .model_emulators import ModelEmulator
from .query_builders.query_filters import StringQueryFilter
from ..entity_providers.model_providers.corefacility_module_provider import CorefacilityModuleProvider


class CorefacilityModuleReader(RawSqlQueryReader):
    """
    Retrieves the information about the corefacility module from the database and sends it to the
    CorefacilityModuleProvider
    """

    _entity_provider = CorefacilityModuleProvider()

    def initialize_query_builder(self):
        """
        Creates common request that will be used for retrieving the list of all modules.

        :return: nothing
        """
        self.items_builder\
            .add_select_expression("core_module.uuid")\
            .add_select_expression("core_module.alias")\
            .add_select_expression("core_module.name")\
            .add_select_expression("core_module.html_code")\
            .add_select_expression("core_module.app_class")\
            .add_select_expression("core_module.user_settings")\
            .add_select_expression("core_module.is_application")\
            .add_select_expression("core_module.is_enabled")\
            .add_data_source("core_module")

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source("core_module")

        for builder in (self.items_builder, self.count_builder):
            builder.data_source.add_join(self.items_builder.JoinType.INNER, "core_entrypoint",
                                         "ON (core_entrypoint.id=core_module.parent_entry_point_id)")

    def apply_entry_point_alias_filter(self, alias):
        """
        Selects only such corefacility modules that attaches to a given entry point

        :param alias: alias of the attaching entry point
        :return: nothing
        """
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("core_entrypoint.alias=%s", alias)

    def create_external_object(self, uuid, alias, name, html_code, app_class, user_settings,
                               is_application, is_enabled):
        """
        Creates an external object that in turn will be transformed to the corefacility module

        :param uuid: the module UUID
        :param alias: the module alias
        :param name: the module name
        :param html_code: the module HTML code
        :param app_class: the application class
        :param user_settings: specific module settings
        :param is_application: defines whether the module is application
        :param is_enabled: defines whether the module is enabled
        :return: an external object that will be transformed by the CorefacilityModuleProvider to an appropriate module.
        """
        return ModelEmulator(
            id=None,
            uuid=UUID(uuid),
            alias=alias,
            name=name,
            app_class=app_class,
            html_code=html_code,
            user_settings=user_settings,
            is_application=is_application,
            is_enabled=is_enabled
        )
