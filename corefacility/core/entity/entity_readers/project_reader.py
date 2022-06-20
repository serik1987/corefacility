from .model_emulators import ModelEmulator, ModelEmulatorFileField
from .query_builders.data_source import SqlTable
from .query_builders.query_filters import SearchQueryFilter, StringQueryFilter
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
        """
        Constructs the default SQL query that will be executed when no filters were applied
        """
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
        """
        Changes the SQL query in such a way as it retrieves projects which name starts from a given string

        :param project_name: the project name to search
        :return: nothing
        """
        for builder in [self.count_builder, self.items_builder]:
            builder.main_filter &= SearchQueryFilter("core_project.name", project_name,
                                                     is_prepared=True, must_start=True)

    def apply_root_group_filter(self, root_group):
        """
        Changes the SQL query in such a way as it retrieves proejct which name starts from a given string

        :param root_group: a root group to filter
        :return: nothing
        """
        if root_group is None:
            return None
        for builder in [self.count_builder, self.items_builder]:
            builder.main_filter &= StringQueryFilter("core_project.root_group_id=%s", root_group.id)

    def apply_user_filter(self, user):
        """
        Changes the SQL query in such a way as it retrieves projects where only certain user has an access

        :param user: the user that wants to gain an access
        :return: nothing
        """
        for builder in [self.items_builder, self.count_builder]:
            builder.data_source\
                .add_join(builder.JoinType.LEFT, SqlTable("core_groupuser", "root_user"),
                          "ON (root_user.group_id=root_group_id AND root_user.user_id=%d)" % int(user.id))\
                .add_join(builder.JoinType.LEFT, SqlTable("core_projectpermission", "acl"),
                          "ON (acl.project_id=core_project.id)")\
                .add_join(builder.JoinType.LEFT, SqlTable("core_accesslevel", "acl_value"),
                          "ON (acl_value.id=acl.access_level_id AND acl_value.alias!='no_access')")\
                .add_join(builder.JoinType.LEFT, SqlTable("core_group", "acl_group"),
                          "ON (acl_group.id=acl.group_id)")\
                .add_join(builder.JoinType.LEFT, SqlTable("core_groupuser", "acl_user"),
                          "ON (acl_user.group_id=acl_group.id AND acl_user.user_id=%d)" % int(user.id))
            # SQL injection is not possible because:
            # a) the user ID is assigned by the DB engine and there is no way how it can be assigned by the user.
            # b) the user ID is transformed into integer by the int() function. Python will never do this with
            #       SQL injections (i.e., any SQL injection will throw ValueError, no transform to integer, no None's).

            builder.main_filter &= \
                StringQueryFilter("acl.group_id IS NULL") | \
                StringQueryFilter("acl_user.user_id IS NOT NULL")
            builder.main_filter &= StringQueryFilter("root_user.user_id=%s", user.id) | \
                StringQueryFilter("acl_value.alias IS NOT NULL")

        self.count_builder.select_expression = \
            self.count_builder.select_total_count("core_project.id", distinct=True)

        self.items_builder\
            .add_select_expression("root_user.is_governor")\
            .add_select_expression(self.items_builder.agg_or("acl_user.is_governor"))\
            .add_select_expression(self.items_builder.agg_or("acl_user.is_governor AND acl_value.alias='full'"))\
            .add_select_expression(self.items_builder.agg_string_concat("acl_value.alias"))\
            .add_group_term("core_project.id")\
            .add_group_term("root_group.id")\
            .add_group_term("governor.id")\
            .add_group_term("root_user.id")

    def apply_application_filter(self, application):
        uuid = str(application.uuid).replace("-", "")
        for builder in (self.items_builder, self.count_builder):
            builder.data_source.add_join(builder.JoinType.LEFT, "core_projectapplication",
                                         "ON (core_projectapplication.project_id=core_project.id AND "
                                         "core_projectapplication.is_enabled)")
            builder.main_filter &= StringQueryFilter("core_projectapplication.application_id=%s", uuid)

    def create_external_object(self, project_id, project_alias, project_avatar,
                               project_name, project_description, project_dir, unix_group,
                               root_group_id, root_group_name,
                               governor_id, governor_login, governor_name, governor_surname,
                               is_root_group_governor=None,
                               is_acl_user=None, is_acl_group_governor=None, acl_access_list=None):
        user_access_level = None
        is_user_governor = None
        if is_root_group_governor is not None or is_acl_group_governor is not None:
            if is_root_group_governor is not None:
                root_group_access_list = {"full"}
            else:
                is_root_group_governor = False
                root_group_access_list = set()

            if is_acl_user is not None:
                is_acl_group_governor = bool(is_acl_group_governor)
                if acl_access_list is None:
                    acl_access_list = set()
                else:
                    acl_access_list = set(acl_access_list.split(","))
            else:
                is_acl_group_governor = False
                acl_access_list = set()

            is_user_governor = is_root_group_governor or is_acl_group_governor
            user_access_level = root_group_access_list | acl_access_list
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
            ),
            is_user_governor=is_user_governor,
            user_access_level=user_access_level
        )
