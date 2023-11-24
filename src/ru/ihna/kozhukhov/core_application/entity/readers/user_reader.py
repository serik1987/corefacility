from ...models import User
from .query_builders.query_filters import StringQueryFilter, SearchQueryFilter

from .sql_model_reader import SqlModelReader
from ..providers.model_providers.user_provider import UserProvider


class UserReader(SqlModelReader):
    """
    Allows to retrieve users from the database
    """

    _entity_model_class = User
    """ The entity model that is used for seeking a proper entity data """

    _entity_provider = UserProvider()
    """
    The instance of the entity provider. When the EntityReader finds an information about
    the entity from the external source that satisfies filter conditions, it calls the
    wrap_entity method of the _entity_provider given here
    """

    _query_debug = False
    """ Set this value as True in case when query execution causes SQL errors """

    def initialize_query_builder(self):
        """
        This function shall call certain methods for the query builder to make
        it to generate proper queries given that no external filters applied

        :return: nothing
        """

        self.items_builder.add_data_source("core_application_user") \
            .add_order_term("surname", null_direction=self.items_builder.NULLS_FIRST) \
            .add_order_term("name", null_direction=self.items_builder.NULLS_FIRST) \
            .add_order_term("login")

        self.count_builder.add_data_source("core_application_user") \
            .add_select_expression(self.count_builder.select_total_count())

    def apply_name_filter(self, value):
        if value == "" or value is None:
            return

        qf = SearchQueryFilter("surname", value) | \
             SearchQueryFilter("name", value) | \
             SearchQueryFilter("login", value)

        self.items_builder.main_filter &= qf
        self.count_builder.main_filter &= qf

    def apply_is_support_filter(self, value):
        qf = StringQueryFilter("is_support") if value else StringQueryFilter("NOT is_support")

        self.items_builder.main_filter &= qf
        self.count_builder.main_filter &= qf

    def apply_is_locked_filter(self, value):
        qf = StringQueryFilter("is_locked") if value else StringQueryFilter("NOT is_locked")

        self.items_builder.main_filter &= qf
        self.count_builder.main_filter &= qf

    def apply_group_filter(self, group):
        """
        Applies the group filter to the project

        :param group: the group for filtration. None means all groups
        :return: nothing
        """
        if group is None:
            return
        for builder in [self.items_builder, self.count_builder]:
            builder.data_source.add_join(builder.JoinType.INNER, "core_application_groupuser",
                                         "ON (core_application_groupuser.user_id=core_application_user.id)")
            builder.main_filter &= \
                StringQueryFilter("core_application_groupuser.group_id=%s", group.id)
