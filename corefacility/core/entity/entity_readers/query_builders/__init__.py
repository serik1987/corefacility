class QueryFragment:
    """
    Query fragment is an object that contains important information about query details
    and allows to construct a certain query fragment (with the aid of the query builder)
    """

    def build_query(self, query_builder):
        """
        Builds a filter for particular query builder

        :param query_builder: the query builder for which the filter shall be built
        :return: a piece of SQL query containing such a filter
        """
        raise NotImplementedError("Please, define the build_filter")

    def build_query_parameters(self):
        """
        The query filter supports prepared SQL query notation.

        :return: list of build query parameters
        """
        raise NotImplementedError("Please, define the build query parameters")
