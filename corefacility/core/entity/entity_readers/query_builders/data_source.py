from core.entity.entity_readers.query_builders import QueryFragment


class DataSource(QueryFragment):
    """
    The data sources are query fragments that are located after the FROM keyword and are responsible
    for telling SQL engine from which table and resource it shall retrieve the data
    """

    __join_list = None

    def __init__(self):
        self.__join_list = list()

    def add_join(self, join_type, data_source, join_condition):
        """
        Inserts the JOIN clause to your SQL data source

        :param join_type: join type. Use JoinType class from your QueryBuilder. Mind that not all join types are
            supported.
        :param data_source: the joined table
        :param join_condition: join condition together with ON and USING keywords (join condition syntax is the same
            for all SQL languages)
        :return: self
        """
        if isinstance(data_source, str):
            data_source = SqlTable(data_source)
        self.__join_list.append((join_type, data_source, join_condition))
        return self

    def build_query(self, query_builder):
        """
        Builds a filter for particular query builder

        :param query_builder: the query builder for which the filter shall be built
        :return: a piece of SQL query containing such a filter
        """
        join_fragments = []
        for join_type, data_source, join_condition in self.__join_list:
            join_fragment = " %s %s %s" % (
                join_type.value,
                data_source.build_query(query_builder),
                join_condition
            )
            join_fragments.append(join_fragment)
        return "".join(join_fragments)

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        parameters = []
        for _, data_source, _ in self.__join_list:
            parameters += list(data_source.build_query_parameters())
        return parameters

class SqlTable(DataSource):
    """
    SQL table is a data source that tells SQL engine to derive the data from a particular table
    """

    def __init__(self, table_name, table_alias=None):
        """
        Initializes the sql table source

        :param table_name: the table name
        :param table_alias: the table alias (i.e., a name after the table is visible for another SQL parts
        """
        super().__init__()
        self.__table_name = table_name
        self.__table_alias = table_alias

    def build_query(self, query_builder):
        """
        Builds a filter for particular query builder

        :param query_builder: the query builder for which the filter shall be built
        :return: a piece of SQL query containing such a filter
        """
        fragment = self.__table_name
        if self.__table_alias is not None:
            fragment += " AS " + self.__table_alias
        return fragment + super().build_query(query_builder)

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        return tuple(super().build_query_parameters())


class Subquery(DataSource):
    """
    Subquery is an SQL query which result table is used as data source for the main SQL query.

    Equivalent construction for all SQL engines:
    SELECT * FROM (SELECT * FROM tbl2 GROUP BY col1) ORDER BY col2
    """

    def __init__(self, query_builder, tbl_alias):
        """
        Initializes the query builder

        :param query_builder: the query builder itself. Be aware that some features available in the main query
            is inavailable in subquery due to SQL syntax specifications.
        :param tbl_alias: the table alias
        """
        super().__init__()
        self.__query_builder = query_builder
        self.__tbl_alias = tbl_alias
        self.__build_result = None

    @property
    def _build_result(self):
        if self.__build_result is None:
            self.__build_result = self.__query_builder.build()
        return self.__build_result

    def build_query(self, query_builder):
        """
        Builds a filter for particular query builder

        :param query_builder: the query builder for which the filter shall be built
        :return: a piece of SQL query containing such a filter
        """
        return "(%s) AS %s" % (self._build_result[0], self.__tbl_alias) + super().build_query(query_builder)

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        return tuple(list(self._build_result[1:]) + list(super().build_query_parameters()))
