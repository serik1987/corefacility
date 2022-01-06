from core.entity.entity_readers.query_builders import QueryFragment


class DataSource(QueryFragment):
    """
    The data sources are query fragments that are located after the FROM keyword and are responsible
    for telling SQL engine from which table and resource it shall retrieve the data
    """

    pass


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
        return fragment

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        return ()


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
        return "(%s) AS %s" % (self._build_result[0], self.__tbl_alias)

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        return self._build_result[1:]
