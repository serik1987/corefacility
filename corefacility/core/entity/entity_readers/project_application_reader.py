import json
from uuid import UUID

from .raw_sql_query_reader import RawSqlQueryReader
from .model_emulators import ModelEmulator
from .query_builders.data_source import SqlTable
from .query_builders.query_filters import StringQueryFilter
from ..entity_providers.model_providers.project_application_provider import ProjectApplicationProvider


class ProjectApplicationReader(RawSqlQueryReader):
    """
    Seeks for information about certain ProjectApplication entity in the database and passes its information
    to the ProjectApplicationProvider
    """

    _entity_provider = ProjectApplicationProvider()

    _lookup_table_name = "core_projectapplication"
    """
    Change this property if get() method will give you something like 'column ... is ambiguous'.
    This will make get() method to add 'WHERE tbl_name.id=%s' instead of 'WHERE id=%s'
    """

    _query_debug = False
    """ Set this value to True to print all queries sent """

    def initialize_query_builder(self):

        self.items_builder\
            .add_select_expression("core_projectapplication.id")\
            .add_select_expression("core_projectapplication.is_enabled")\
            .add_select_expression("core_module.uuid")\
            .add_select_expression("core_module.alias")\
            .add_select_expression("core_module.name")\
            .add_select_expression("core_module.html_code")\
            .add_select_expression("core_module.is_application")\
            .add_select_expression("core_module.app_class")\
            .add_select_expression("core_module.is_enabled")\
            .add_select_expression("core_module.user_settings")\
            .add_select_expression("core_project.id")\
            .add_select_expression("core_project.alias")\
            .add_select_expression("core_project.avatar")\
            .add_select_expression("core_project.name")\
            .add_select_expression("core_project.description")\
            .add_select_expression("core_project.project_dir")\
            .add_select_expression("core_project.unix_group")\
            .add_select_expression("root_group.id")\
            .add_select_expression("root_group.name")\
            .add_select_expression("governor.id")\
            .add_select_expression("governor.login")\
            .add_select_expression("governor.name")\
            .add_select_expression("governor.surname") \
            .add_order_term("core_projectapplication.id", self.items_builder.ASC)

        self.count_builder.add_select_expression(self.count_builder.select_total_count())

        for builder in (self.items_builder, self.count_builder):
            builder\
                .add_data_source("core_projectapplication")
            builder.data_source \
                .add_join(builder.JoinType.INNER, "core_module",
                          "ON (core_module.uuid=core_projectapplication.application_id)") \
                .add_join(builder.JoinType.INNER, "core_project",
                          "ON (core_project.id=core_projectapplication.project_id)")

        self.items_builder.data_source\
            .add_join(self.items_builder.JoinType.INNER, SqlTable("core_group", "root_group"),
                      "ON (root_group.id=root_group_id)") \
            .add_join(self.items_builder.JoinType.INNER, SqlTable("core_groupuser", "governor_info"),
                      "ON (governor_info.group_id=root_group_id AND governor_info.is_governor)") \
            .add_join(self.items_builder.JoinType.INNER, SqlTable("core_user", "governor"),
                      "ON (governor_info.user_id=governor.id)")

    def apply_entity_is_enabled_filter(self, is_enabled):
        current_filter = StringQueryFilter("core_projectapplication.is_enabled")
        if not is_enabled:
            current_filter = ~current_filter
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= current_filter

    def apply_project_filter(self, project):
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("core_project.id=%s", project.id)

    def apply_application_filter(self, app):
        uuid = str(app.uuid).replace("-", "")
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("core_module.uuid=%s", uuid)

    def apply_application_is_enabled_filter(self, is_enabled):
        current_filter = StringQueryFilter("core_module.is_enabled")
        if not is_enabled:
            current_filter = ~current_filter
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= current_filter

    def apply_application_alias_filter(self, application_alias):
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("core_module.alias=%s", application_alias)

    def create_external_object(self, entity_id, is_enabled, module_uuid, module_alias, module_name, module_html_code,
                               module_is_application, module_app_class, module_is_enabled, module_user_settings,
                               project_id, project_alias, project_avatar, project_name, project_description,
                               project_dir, unix_group,
                               root_group_id, root_group_name,
                               governor_id, governor_login, governor_name, governor_surname):
        if isinstance(module_user_settings, str):
            try:
                module_user_settings = json.loads(module_user_settings)
            except json.JSONDecodeError:
                module_user_settings = {}
        if isinstance(module_uuid, str):
            module_uuid = UUID(module_uuid)
        return ModelEmulator(
            id=entity_id,
            is_enabled=is_enabled,
            application=ModelEmulator(
                uuid=module_uuid,
                alias=module_alias,
                name=module_name,
                html_code=module_html_code,
                is_application=module_is_application,
                is_enabled=module_is_enabled,
                app_class=module_app_class,
                user_settings=module_user_settings
            ),
            project=ModelEmulator(
                id=project_id,
                alias=project_alias,
                avatar=project_avatar,
                name=project_name,
                description=project_description,
                project_dir=project_dir,
                unix_group=unix_group,
                root_group=ModelEmulator(
                    id=root_group_id,
                    name=root_group_name,
                    governor=ModelEmulator(
                        id=governor_id,
                        login=governor_login,
                        name=governor_name,
                        surname=governor_surname
                    )
                )
            )
        )
