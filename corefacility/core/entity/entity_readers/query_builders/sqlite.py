from .base import QueryBuilder


class SqliteQueryBuilder(QueryBuilder):
    """
    Implements query builder for SQLite queries
    """

    def build_limit(self):
        """
        Constructs the LIMIT expression

        :return: a string containing the limit expression
        """
        query = None
        if self._limit:
            query = "LIMIT %d OFFSET %d" % (self._limit, self._offset)
        return query
