from .base import QueryBuilder


class MysqlQueryBuilder(QueryBuilder):
    """
    Implements query builder for MySQL queries
    """

    _nulls_direction_support = False

    @classmethod
    def select_string_concatenation(cls, *args):
        """
        Returns an SQL query expression that concatenates different strings

        :param args: strings to concatenate (all are SQL expressions)
        :return: SQL query fragment for string concatenation
        """
        return "CONCAT(%s)" % ", ".join(args)

    def build_limit(self):
        """
        Constructs the LIMIT expression

        :return: a string containing the limit expression
        """
        query = None
        if self._limit:
            query = "LIMIT %d, %d" % (self._offset, self._limit)
        return query
