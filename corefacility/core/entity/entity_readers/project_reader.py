from .model_emulators import ModelEmulator, ModelEmulatorFileField
from .query_builders.data_source import SqlTable
from .query_builders.query_filters import SearchQueryFilter
from .raw_sql_query_reader import RawSqlQueryReader
from ..entity_providers.model_providers.project_provider import ProjectProvider


class ProjectReader(RawSqlQueryReader):
    """
    Implements the project reader
    """

    _entity_provider = ProjectProvider()
    """
    The instance of the entity provider. When the EntityReader finds an information about
    the entity from the external source that satisfies filter conditions, it calls the
    wrap_entity method of the _entity_provider given here
    """

    _lookup_table_name = "core_project"
    """
    Change this property if get() method will give you something like 'column ... is ambiguous'.
    This will make get() method to add 'WHERE tbl_name.id=%s' instead of 'WHERE id=%s'
    """

    _query_debug = False
    """ Set this value to True for troubleshooting. """

    def initialize_query_builder(self):
        self.items_builder\
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
            .add_select_expression("governor.surname")\
            .add_data_source("core_project")\
            .add_order_term("core_project.name")
        self.items_builder.data_source\
            .add_join(self.items_builder.JoinType.INNER, SqlTable("core_group", "root_group"),
                      "ON (root_group.id=root_group_id)")\
            .add_join(self.items_builder.JoinType.INNER, SqlTable("core_groupuser", "governor_info"),
                      "ON (governor_info.group_id=root_group_id AND governor_info.is_governor)")\
            .add_join(self.items_builder.JoinType.INNER, SqlTable("core_user", "governor"),
                      "ON (governor_info.user_id=governor.id)")

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count()) \
            .add_data_source("core_project")

    def apply_name_filter(self, project_name):
        for builder in [self.count_builder, self.items_builder]:
            builder.main_filter &= SearchQueryFilter("core_project.name", project_name,
                                                     is_prepared=True, must_start=True)

    def create_external_object(self, project_id, project_alias, project_avatar,
                               project_name, project_description, project_dir, unix_group,
                               root_group_id, root_group_name,
                               governor_id, governor_login, governor_name, governor_surname):
        return ModelEmulator(
            id=project_id,
            alias=project_alias,
            avatar=ModelEmulatorFileField(name=project_avatar),
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
