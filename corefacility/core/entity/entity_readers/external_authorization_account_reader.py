from .raw_sql_query_reader import RawSqlQueryReader
from .query_builders.query_filters import StringQueryFilter


class ExternalAuthorizationAccountReader(RawSqlQueryReader):
    """
    Reads the information about the external authorization account from the database and
    sends it to the entity set
    """

    @property
    def lookup_table_name(self):
        """
        Name of the lookup table
        """
        if self._lookup_table_name is None:
            raise NotImplementedError("The _lookup_table_name property must be set for the "
                                      "ExternalAuthorizationAccountReader subclasses")
        return self._lookup_table_name

    def initialize_query_builder(self):
        self.items_builder\
            .add_select_expression("%s.id" % self.lookup_table_name)\
            .add_select_expression("core_user.id")\
            .add_select_expression("core_user.login")\
            .add_select_expression("core_user.name")\
            .add_select_expression("core_user.surname")\
            .add_select_expression("core_user.email")\
            .add_select_expression("core_user.phone")\
            .add_select_expression("core_user.is_locked")\
            .add_select_expression("core_user.is_superuser")\
            .add_data_source(self.lookup_table_name)
        self.items_builder.data_source.add_join(self.items_builder.JoinType.INNER, "core_user",
                                                "ON (core_user.id=%s.user_id)" % self.lookup_table_name)

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source(self.lookup_table_name)

    def apply_user_filter(self, user):
        for builder in [self.items_builder, self.count_builder]:
            builder.main_filter &= StringQueryFilter("%s.user_id=%%s" % self.lookup_table_name, user.id)
