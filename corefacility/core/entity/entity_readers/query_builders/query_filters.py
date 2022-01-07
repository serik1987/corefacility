from core.entity.entity_readers.query_builders import QueryFragment


class QueryFilter(QueryFragment):
    """
    Query filters are SQL query fragments that contain in WHERE clause and are responsible for data filtration.
    """

    def __invert__(self):
        """
        Returns the negative query filter
        """
        return NegotiationQueryFilter(self)

    def __and__(self, other):
        """
        provides the and operation on query filters

        :param other: the other query filter
        :return: the operation result
        """
        return AndQueryFilter(self, other)

    def __or__(self, other):
        """
        Provides the or operation on query filters

        :param other: the other query filter
        :return: the operation result
        """
        return OrQueryFilter(self, other)


class StringQueryFilter(QueryFilter):
    """
    This is a raw SQL query filter that allows you to induce raw SQL query fragments.

    Use such filter in such situation where filter expression syntax is similar for all SQL engines
    (so called 'comparison expressions' is exactly such a case)
    """

    def __init__(self, query_fragment, *args):
        """
        Initializes the string query filter

        :param query_fragment: the query fragment to embed. Use prepared query notations is you need
        :param args: the builder arguments if you used prepared query notation
        """
        self.__query_fragment = query_fragment
        self.__query_parameters = args

    def build_query(self, query_builder):
        """
        Builds a filter for particular query builder

        :param query_builder: the query builder for which the filter shall be built
        :return: a piece of SQL query containing such a filter
        """
        return self.__query_fragment

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        return self.__query_parameters


class UnaryQueryFilter(QueryFilter):
    """
    The query filter that is organized from another query filter by applying some unary operation
    (e.g., negotiation, contains, starts with and ends with query filters
    """

    def __init__(self, qf: QueryFilter):
        """
        Initializes the query filter

        :param qf: another query filter to which the operator must be applied
        """
        self._query_filter = qf

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        return self._query_filter.build_query_parameters()


class NegotiationQueryFilter(UnaryQueryFilter):
    """
    The query filter providers negotiation operation
    """

    def build_query(self, query_builder):
        """
        Builds the query filter parameter

        :param query_builder: the query builder to use
        :return: nothing
        """
        return "NOT (%s)" % self._query_filter.build_query(query_builder)


class BinaryQueryFilter(QueryFilter):
    """
    The binary query filter is a query filter that is a result of application of some binary filter operation
    (e.g., AND, OR)
    """

    _binary_operator = None

    def __init__(self, *query_filters):
        """
        initializes the query filter

        :param query_filters: list of query filters that were used as arguments
        """
        self._query_filters = list(query_filters)

    @property
    def binary_operator(self):
        if self._binary_operator is None:
            raise NotImplementedError("The _binary_operator property for the query filter must be applied")
        return self._binary_operator

    def add(self, query_filter):
        """
        Adds query to the expression

        :param query_filter: the filter to add
        :return: self
        """
        self._query_filters.append(query_filter)
        return self

    def build_query(self, query_builder):
        """
        Builds a filter for particular query builder

        :param query_builder: the query builder for which the filter shall be built
        :return: a piece of SQL query containing such a filter
        """
        if len(self._query_filters) == 0:
            return ""
        return self.binary_operator.join(["(%s)" % f.build_query(query_builder) for f in self._query_filters])

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        qp = []
        for f in self._query_filters:
            qp.extend(f.build_query_parameters())
        return qp


class AndQueryFilter(BinaryQueryFilter):
    """
    The query filter implements binary AND operation on the rest of query filters
    """

    _binary_operator = " AND "

    def __and__(self, other):
        """
        Overrides the AND query filter operation

        :param other: the other query filter
        :return: self
        """
        self.add(other)
        return self


class OrQueryFilter(BinaryQueryFilter):
    """
    The query filter implements binary OR operation on the rest of query filters
    """

    _binary_operator = " OR "

    def __or__(self, other):
        self.add(other)
        return self


class SearchQueryFilter(QueryFilter):
    """
    Search query filters select all rows containing a given text in certain cell. The cell contents should not match
    a search string but should contain such a string.
    """

    def __init__(self, col, value, is_prepared=True, must_start=False, must_finish=False):
        """
        Initializes the query filter

        :param col: table column to look for
        :param value: searching value
        :param is_prepared: if True the value shall be sent to the SQL server by means of prepared statement.
            if False this is not required.
        :param must_start: if True the search string must be exactly at the beginning of the text. If False  this
            is not necessary
        :param must_finish: if True the search string must be exactly at the end of the text. If False this is not
            necessary.
        """
        self.__col = col
        self.__value = value
        self.__is_prepared = is_prepared
        self.__must_start = must_start
        self.__must_finish = must_finish

    def build_query(self, query_builder):
        """
        Builds a filter for particular query builder

        :param query_builder: the query builder for which the filter shall be built
        :return: a piece of SQL query containing such a filter
        """
        if self.__is_prepared:
            concat_list = ["%s"]
            if not self.__must_start:
                concat_list.insert(0, "'%%'")
            if not self.__must_finish:
                concat_list.append("'%%'")
            query_term = query_builder.select_string_concatenation(*concat_list)
        else:
            query_term = "'%%%s%%'" % self.__value
        return "%s LIKE %s" % (self.__col, query_term)

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        if self.__is_prepared:
            return self.__value,
        else:
            return ()
