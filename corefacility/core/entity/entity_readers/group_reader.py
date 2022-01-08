from core.entity.entity_providers.model_providers.group_provider import GroupProvider
from core.entity.entity_readers.model_emulators import ModelEmulator
from core.entity.entity_readers.query_builders.data_source import SqlTable
from core.entity.entity_readers.raw_sql_query_reader import RawSqlQueryReader


class GroupReader(RawSqlQueryReader):
    """
    Picks up scientific group data from the database
    """

    _entity_provider = GroupProvider()
    """ The group provider will be used to wrap groups """

    _lookup_table_name = "core_group"

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
            .add_select_expression("core_group.id") \
            .add_select_expression("core_group.name") \
            .add_select_expression("core_user.id") \
            .add_select_expression("core_user.login") \
            .add_select_expression("core_user.name") \
            .add_select_expression("core_user.surname") \
            .add_data_source("core_group") \
            .add_order_term("core_group.name")
        self.items_builder.data_source\
            .add_join(self.items_builder.JoinType.INNER, SqlTable("core_groupuser", "governors"),
                      "ON (governors.group_id=core_group.id AND governors.is_governor)")\
            .add_join(self.items_builder.JoinType.INNER, "core_user",
                      "ON (core_user.id=governors.user_id)")

    def create_external_object(self, group_id, group_name,
                               governor_id, governor_login, governor_name, governor_surname):
        return ModelEmulator(
            id=group_id,
            name=group_name,
            governor=ModelEmulator(
                id=governor_id,
                login=governor_login,
                name=governor_name,
                surname=governor_surname
            )
        )
