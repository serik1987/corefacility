import json
from uuid import UUID

from .query_builders.base import QueryBuilder
from .raw_sql_query_reader import RawSqlQueryReader
from .query_builders.data_source import SqlTable
from .model_emulators import ModelEmulator
from .query_builders.query_filters import StringQueryFilter
from ..entity_exceptions import CorefacilityModuleAutoloadFailedException
from ..entity_providers.model_providers.corefacility_module_provider import CorefacilityModuleProvider


class CorefacilityModuleReader(RawSqlQueryReader):
    """
    Retrieves the information about the corefacility module from the database and sends it to the
    CorefacilityModuleProvider
    """

    _entity_provider = CorefacilityModuleProvider()

    _query_debug = False

    _lookup_table_name = "core_module"

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
            .add_data_source("core_module")\
            .add_order_term("core_module.name", QueryBuilder.ASC)

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source("core_module")

        for builder in (self.items_builder, self.count_builder):
            builder.data_source.add_join(builder.JoinType.LEFT, "core_entrypoint",
                                         "ON (core_entrypoint.id=core_module.parent_entry_point_id)")

    def apply_is_root_module_filter(self, filter_value):
        """
        The filter selects core module only

        :param filter_value: True - select core module only, False - select all modules except core module
        :return: nothing
        """
        if filter_value:
            query_filter = StringQueryFilter("core_module.parent_entry_point_id IS NULL")
        else:
            query_filter = StringQueryFilter("core_module.parent_entry_point_id IS NOT NULL")
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= query_filter

    def apply_entry_point_filter(self, entry_point):
        """
        The filter selects modules that are attached to a certain entry point.
        Note that information connected to a certain entry point must be preloaded.

        :param entry_point: an entry point to which modules shall be attached (An EntryPoint instance)
        :return: nothing
        """
        entry_point_id = entry_point.id
        if not isinstance(entry_point_id, int):
            raise CorefacilityModuleAutoloadFailedException("id", entry_point)
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("core_module.parent_entry_point_id = %s", entry_point_id)

    def apply_is_enabled_filter(self, is_enabled):
        filter_clause = StringQueryFilter("core_module.is_enabled")
        if not is_enabled:
            filter_clause = ~filter_clause
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= filter_clause

    def apply_is_application_filter(self, is_application):
        filter_clause = StringQueryFilter("core_module.is_application")
        if not is_application:
            filter_clause = ~filter_clause
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= filter_clause

    def apply_project_filter(self, project):
        for builder in (self.items_builder, self.count_builder):
            builder.data_source.add_join(builder.JoinType.LEFT, "core_projectapplication",
                                         "ON (core_projectapplication.application_id=core_module.uuid AND "
                                         "core_projectapplication.is_enabled)")
            builder.main_filter &= StringQueryFilter("core_projectapplication.project_id=%s", project.id)

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
        if isinstance(user_settings, str):
            try:
                user_settings = json.loads(user_settings)
            except json.JSONDecodeError:
                user_settings = {}
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        emulator = ModelEmulator(
            id=None,
            uuid=uuid,
            alias=alias,
            name=name,
            app_class=app_class,
            html_code=html_code,
            user_settings=user_settings,
            is_application=bool(is_application),
            is_enabled=bool(is_enabled),
        )
        return emulator
