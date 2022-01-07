from core.entity.entity_exceptions import EntityFeatureNotSupported, EntityNotFoundException
from core.entity.entity_readers.query_builders.data_source import SqlTable


class QueryBuilder:
    """
    This is the base class that facilitates query building.

    The main problem with the multi-database is different database engines has different SQL query syntax.
    This makes trouble for entity readers based on raw SQL queries. In order to overcome such troubles we have
    made an SQL query builder that provides the interface negotiation.

    The Query builder support SELECT queries only. Use Django model manager to send another types of queries.
    """

    ASC = 0
    DESC = 1
    _order_direction_fragments = {ASC: 'ASC', DESC: 'DESC'}

    DEFAULT_NULL_ORDER = 0
    NULLS_FIRST = 1
    NULLS_LAST = 2
    _null_direction_fragments = {DEFAULT_NULL_ORDER: None, NULLS_FIRST: " NULLS FIRST", NULLS_LAST: " NULLS LAST"}
    _nulls_direction_support = True

    def __init__(self):
        """
        Initializes the query builder
        """
        self._common_table_expressions = []
        self._recursive_expressions = False
        self._is_distinct = None
        self._distinct_expression = None
        self._select_expressions = []
        self._data_sources = []
        self._main_filter = None
        self._union_type = None
        self._union_query = None
        self._order_terms = []
        self._limit = None
        self._offset = None
        self.__query_parameters = None

    @property
    def is_distinct(self):
        """
        Defines whether the query shall return DISTINCT results

        :return: True if the query shall return DISTINCT result
        """
        return self._distinct_expression

    @property
    def main_filter(self):
        """
        The main query filter. Don't afraid of being manipulated by this filter to add some extra WHERE clauses
        """
        return self._main_filter

    @main_filter.setter
    def main_filter(self, value):
        """
        The main query filter. Don't afraid of being manipulated by this filter to add some extra WHERE clauses
        """
        self._main_filter = value

    @property
    def attached_query_builder(self):
        """
        The query builder attached by means of attach_query function (UNION expression will be used)
        """
        return self._union_query

    @property
    def data_source(self):
        """
        The last data sources added by means of the add_data_source routine. Use this object to call join_data
        method that inserts the LEFT JOIN, INNER JOIN or CROSS JOIN clause.

        See the following manual on various join types:
        https://dataschool.com/how-to-teach-people-sql/sql-join-types-explained-visually/

        But bear in mind that some join types are not supported in particular SQL engines. If you apply them you
        will get AttributeError

        Outer join: builder.data_source |= ("another_table", "ON left.col1=right.col2")
        Inner join: builder.data_source &= ("another_table", "ON left.col1=right.col2")
        Left join: builder.data_source <<= ("another_table", "ON left.col1=right.col2")
        Right join: builder.data_source >>= ("another_table", "ON left.col1=right.col2")
        Union join: builder.data_source += ("another_table", "ON left.col1=right.col2")
        Cross join: builder.data_source *= ("another_table", "ON left.col1=right.col2")

        If you want to use table alias you can write more complicated things:
        Outer join:
        builder.data_source |= (SqlTable(original_name, table_alias="other_name"), "ON left.col1=right.col2")
        Inner join:
        builder.data_source &= (SqlTable(original_name, table_alias="other_name"), "ON left.col1=right.col2")
        Left join:
        builder.data_source <<= (SqlTable(original_name, table_alias="other_name"), "ON left.col1=right.col2")
        Right join:
        builder.data_source >>= (SqlTable(original_name, table_alias="other_name"), "ON left.col1=right.col2")
        Union join:
        builder.data_source += (SqlTable(original_name, table_alias="other_name"), "ON left.col1=right.col2")
        Cross join:
        builder.data_source *= (SqlTable(original_name, table_alias="other_name"), "ON left.col1=right.col2")

        In any way, the first element pf the tuple must be an instance of DataSource or string that will
        be converted to SqlTable. The second element is join condition that is absolutely the same for all
        SQL languages. If you use another data source than the SqlTable there is no problem to add such a data source
        to your SQL query string but there is no guarantee that such a query will be understood by your SQL engine.
        Refer to your SQL language documentation on whether you can do this or not.

        According to SQL query documentation the following joins only were supported. In case when such a join type
        is not supported you will receive the EntityFeatureNotSupported exception

        SQL engine  Inner join  Left join   Right join  Outer join  Union join  Cross join
        --------------------------------------------------------------------------------------
        PostgreSQL  yes         yes         yes         yes         no          yes
        MySQL       yes         yes         yes         no          no          yes
        SQLite      yes         yes         no          no          no          yes
        """
        return self._data_sources[-1]

    @data_source.setter
    def data_source(self, value):
        """
        The last data sources added by means of the add_data_source routine. Use this object to call join_data
        method that inserts the LEFT JOIN, INNER JOIN or CROSS JOIN clause.
        """
        self._data_sources[-1] = value

    def add_common_table_expression(self, expr):
        """
        Adds the common table expression

        :param expr: some common table expression
        :return: link to this class
        """
        self._common_table_expressions.append(expr)
        return self

    def recursive_common_table_expressions(self):
        """
        Tells query builder that the table expression is recursive

        :return: link to this class
        """
        self._recursive_expressions = True
        return self

    def distinct(self, expression=None):
        """
        tells SQL engine to retrieve DISTINCT rows only (see DISTINCT keyword for your SQL query documentation)

        :param expression: when this is not None, PostgreSQL query builder will add ON clause after the DISTINCT
        keyword while other
        :return: self
        """
        self._is_distinct = True
        if expression is not None:
            raise EntityFeatureNotSupported()
        return self

    def no_distinct(self):
        """
        tells SQL engine to retrieve ALL rows including duplicates.
        When no distrinct and no_distinct functions were called, The behavior of SQL engine is defined solely
        by its documentation. This means that no additional keyword will be inserted between SELECT and
        the query result list

        :return: self
        """
        self._is_distinct = False
        self._distinct_expression = None

    def add_select_expression(self, expr, alias=None):
        """
        Adds the select expression (a term between SELECT and FROM keywords).
        Don't afraid to use build-in select_**** since they provide platform independent selection routines.
        They are always either static or class methods

        :param expr: expression to select
        :param alias: resultant column name
        :return: nothing
        """
        if alias is not None:
            expr += " AS " + alias
        self._select_expressions.append(expr)

    @staticmethod
    def select_total_count():
        """
        SELECT expression that will count total row number in 99.9999999% of cases.
        """
        return "COUNT(*)"

    @classmethod
    def select_string_concatenation(cls, *args):
        """
        Returns an SQL query expression that concatenates different strings

        :param args: strings to concatenate (all are SQL expressions)
        :return: SQL query fragment for string concatenation
        """
        raise NotImplementedError("QueryBuilder.select_string_concatenation is not implemented")

    def add_data_source(self, data_source):
        """
        Adds data source to the query.

        Data sources are special query fragment that are located exactly after FROM keyword and define the sources
        from which the data shall be taken.

        If you don't apply this function '*' will be used as a total select expression.

        :param data_source: the data source or str if you want to add SqlTable with a given name and no alias.
        :return: self
        """
        if isinstance(data_source, str):
            data_source = SqlTable(data_source)
        self._data_sources.append(data_source)
        return self

    def set_main_filter(self, filter):
        """
        Sets the query main filter

        :param filter: query filter (must be a properly initialized instance of the QueryFilter)
        :return: the object itself
        """
        self._main_filter = filter
        return self

    def attach_query(self, union_type, query_builder):
        """
        Allows to attach another query builder to this query builder by making so called 'compound select' query
        (UNION keyword).
        Be attentive that not all query builders can be attached to each other. If two query builders are inattachable
        you will get an SQL syntax error. If you do so turn _query_debug property in your entity reader and
        refer to your SQL documentation to check how to reorganize query_builder in such a way as to make your
        query syntax correct.

        In any way, ordering and limitation must not be applied in the query builder passed as query_builder argument.

        You can attach your query just once. Next call of the function will cancel the previous one. However, you
        can attach all further queries to another query_builder that you have passed as an argument. Such a builder
        is accessible via 'attached_query_builder' property.

        :param union_type: 'UNION' includes a row in the query result if and only if the result exists in at least
        one subquery, 'INTERSECT' includes a row in the query result if and only if the result exists in all subqueries.
        'EXCEPT' includes a row in the query result if the result exists in current query but is absent in the
        query_builder. 'UNION ALL', 'INTERSECT ALL', 'EXCEPT ALL' will do the same but will also include duplicates.
        Please, bear in mind that not all options are supported in all database engines that could make the SQL syntax
        error
        :param query_builder: the query_builder to attach
        :return: self
        """
        self._union_type = union_type
        self._union_query = query_builder
        return self

    def add_order_term(self, col_name, direction=ASC, null_direction=DEFAULT_NULL_ORDER):
        """
        Adds ordering condition that allows to retrieve properly sorted results (ORDER BY).

        :param col_name: column name in the resultant table under which the ordering shall be performed
        :param direction: ordering direction. Available option: QueryBuilder.ASC, QueryBuilder.DESC
        :param null_direction: Defines how the MySQL engine will order NULL values for all SQL engines except MySQL.
            Useless in MySQL. Available values: QueryBuilder.DEFAULT, QueryBuilder.NULLS_FIRST, QueryBuilder.NULLS_LAST
        :return: self
        """
        self._order_terms.append((col_name, direction, null_direction))
        return self

    def limit(self, offset, limit):
        """
        Restricts the number of result rows in the query.

        Despite the selected SQL engine positive offsets and counts are supported. Using negative ones will result
        to EntityNotFoundException

        :param offset: index of the first row to output. The argument will automatically be transformed to integer
        :param limit: total number of rows to output. The argument will automatically be transformed to integer
        :return: self
        """
        self._offset = int(offset)
        self._limit = int(limit)
        if self._offset < 0 or self._limit < 0:
            raise EntityNotFoundException()
        return self

    def build(self):
        """
        Builds the SQL query

        :return: arguments for Manager.raw as well as for cursor.execute functions
        """
        self.__query_parameters = list()
        raw_query_fragments = [
            self.build_common_table_expressions(),
            "SELECT", self.build_distinct_conditions(), self.build_select_expressions(),
            self.build_from_expressions(),
            self.build_where_expression(),
            self.build_group_by_expression(),
            self.build_union_expression(),
            self.build_order_by(),
            self.build_limit()
        ]
        query_fragments = [fragment for fragment in raw_query_fragments if fragment is not None]
        query = " ".join(query_fragments)
        return query, *self.__query_parameters

    def build_common_table_expressions(self):
        """
        Constructs all common table expressions

        :return: the query fragment
        """
        if len(self._common_table_expressions) == 0:
            return None
        cte_operator = "WITH RECURSIVE " if self._recursive_expressions else "WITH "
        return cte_operator + ",".join(self._common_table_expressions)

    def build_distinct_conditions(self):
        """
        Returns the 'DISTINCT keyword is necessary
        """
        if self._is_distinct is None:
            return None
        return "DISTINCT" if self._is_distinct else "ALL"

    def build_select_expressions(self):
        """
        Construct list of all select expressions that shall be presented before FROM query keyword

        :return: the query fragment
        """
        if len(self._select_expressions) > 0:
            query_fragment = ", ".join(self._select_expressions)
        else:
            query_fragment = "*"
        return query_fragment

    def build_from_expressions(self):
        """
        Builds the FROM expression. The resultant string shall also contain JOIN expression since
        such expression is within the FROM block according to PostgreSQL, MySQL and SQLite query documentation.

        :return: a string containing FROM expression
        """
        query_fragment = None
        if len(self._data_sources) > 0:
            from_fragments = []
            for source in self._data_sources:
                from_fragments.append(source.build_query(self))
                self.__query_parameters.extend(source.build_query_parameters())
            query_fragment = "FROM " + ", ".join(from_fragments)
        return query_fragment

    def build_where_expression(self):
        """
        Constructs the query WHERE expression based on filter settings

        :return: WHERE expression
        """
        query = None
        if self._main_filter is not None:
            query_fragment = self._main_filter.build_query(self)
            if query_fragment is not None and query_fragment != "":
                query = "WHERE " + query_fragment
            self.__query_parameters.extend(self._main_filter.build_query_parameters())
        return query

    def build_group_by_expression(self):
        """
        Constructs the query's GROUP BY fragment

        :return: the GROUP BY expression
        """
        return None

    def build_union_expression(self):
        """
        Constructs the UNION expression

        :return: the query
        """
        query = None
        if self._union_query is not None:
            another_query = self._union_query.build()
            self.__query_parameters.append(another_query[1:])
            query = "%s %s" % (self._union_type, another_query[0])
        return query

    def build_order_by(self):
        """
        Constructs the ORDER BY expression

        :return: a string containing the ORDER BY expression
        """
        if len(self._order_terms) == 0:
            return None
        else:
            query_terms = []
            for order_term in self._order_terms:
                query_term = "%s %s" % (order_term[0], self._order_direction_fragments[order_term[1]])
                if self._nulls_direction_support and self._null_direction_fragments[order_term[2]] is not None:
                    query_term += self._null_direction_fragments[order_term[2]]
                query_terms.append(query_term)
            return "ORDER BY " + ", ".join(query_terms)

    def build_limit(self):
        """
        Constructs the LIMIT expression

        :return: a string containing the limit expression
        """
        raise NotImplementedError("build_limit is not implemented for your query builder")

    def __str__(self):
        """
        Allows to print the currently building query in order to check why the query actual results
        are not satisfiable

        :return:a string containing short query information
        """
        query = self.build()
        return "Query: %s\nBind arguments: %s" % (query[0], query[1:])
