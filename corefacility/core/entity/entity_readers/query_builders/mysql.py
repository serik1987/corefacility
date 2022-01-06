from .base import QueryBuilder


class MysqlQueryBuilder(QueryBuilder):
    """
    Implements query builder for MySQL queries
    """

    _nulls_direction_support = False

    def build_limit(self):
        """
        Constructs the LIMIT expression

        :return: a string containing the limit expression
        """
        query = None
        if self._limit:
            query = "LIMIT %d, %d" % (self._offset, self._limit)
        return query
