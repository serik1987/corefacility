from ..providers.model_providers.group_provider import GroupProvider
from .model_emulators import ModelEmulator, ModelEmulatorFileField
from .query_builders.data_source import SqlTable
from .query_builders.query_filters import SearchQueryFilter, StringQueryFilter
from .raw_sql_query_reader import RawSqlQueryReader


class GroupReader(RawSqlQueryReader):
    """
    Picks up scientific group data from the database
    """

    _entity_provider = GroupProvider()
    """ The group provider will be used to wrap groups """

    _lookup_table_name = "core_application_group"

    _query_debug = False

    def initialize_query_builder(self):
        """
        This function shall call certain methods for the query builder to make
        it to generate proper queries given that no external filters applied

        :return: nothing
        """

        self.count_builder \
            .add_select_expression(self.count_builder.select_total_count()) \
            .add_data_source("core_group")

        self.items_builder\
            .add_select_expression("core_application_group.id") \
            .add_select_expression("core_application_group.name") \
            .add_select_expression("core_application_user.id") \
            .add_select_expression("core_application_user.login") \
            .add_select_expression("core_application_user.name") \
            .add_select_expression("core_application_user.surname") \
            .add_select_expression("core_application_user.avatar") \
            .add_data_source("core_application_group") \
            .add_order_term("core_application_group.name")
        self.items_builder.data_source\
            .add_join(
                self.items_builder.JoinType.INNER,
                SqlTable("core_application_groupuser", "governors"),
                "ON (governors.group_id=core_group.id AND governors.is_governor)")\
            .add_join(self.items_builder.JoinType.INNER, "core_user",
                      "ON (core_application_user.id=governors.user_id)")
    
    def apply_name_filter(self, search_string):
        """
        Applies the name filter to the object
        
        :param search_string: a string to search
        :return: nothing
        """
        qf = SearchQueryFilter("core_application_group.name", search_string, must_start=True)
        self.items_builder.main_filter &= qf
        self.count_builder.main_filter &= qf

    def apply_user_filter(self, user):
        """
        Applies the user to the object

        :param user: the user to apply
        :return: nothing
        """
        user_source = "core_application_groupuser"
        user_condition = "ON (core_application_groupuser.group_id=core_group.id)"
        user_filter = StringQueryFilter("core_application_groupuser.user_id=%s", user.id)

        for builder in [self.items_builder, self.count_builder]:
            builder.data_source.add_join(builder.JoinType.INNER, user_source, user_condition)
            builder.main_filter &= user_filter

    def apply_governor_filter(self, governor):
        if governor is not None:
            self.count_builder.data_source\
                .add_join(
                    self.items_builder.JoinType.INNER,
                    SqlTable("core_application_groupuser", "governors"),
                    "ON (governors.group_id=core_group.id AND governors.is_governor)")
            for builder in [self.items_builder, self.count_builder]:
                builder.main_filter &= StringQueryFilter("governors.user_id=%s", governor.id)

    def create_external_object(self, group_id, group_name,
                               governor_id, governor_login, governor_name, governor_surname, governor_avatar):
        return ModelEmulator(
            id=group_id,
            name=group_name,
            governor=ModelEmulator(
                id=governor_id,
                login=governor_login,
                name=governor_name,
                surname=governor_surname,
                avatar=ModelEmulatorFileField(name=governor_avatar)
            )
        )
