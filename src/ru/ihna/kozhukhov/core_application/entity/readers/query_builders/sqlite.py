from enum import Enum

from .base import QueryBuilder


class SqliteQueryBuilder(QueryBuilder):
    """
    Implements query builder for SQLite queries
    """

    @classmethod
    def agg_string_concat(cls, col_name):
        return "GROUP_CONCAT(%s)" % col_name

    class JoinType(Enum):
        """
        Defines a particular join type
        """
        INNER = "INNER JOIN"
        LEFT = "LEFT JOIN"
        OUTER = "OUTER JOIN"
        CROSS = "CROSS JOIN"

    @classmethod
    def select_string_concatenation(cls, *args):
        """
        Returns an SQL query expression that concatenates different strings

        :param args: strings to concatenate (all are SQL expressions)
        :return: SQL query fragment for string concatenation
        """
        return " || ".join(args)

    @classmethod
    def json_object_aggregation(cls, name, value):
        """
        Returns an SQL query expression that aggregates name/value pairs containing in different rows as a single
        JSON object. Values can be NULL's but not names

        :param name: expression or a column name that will be used as JSON keys
        :param value: expression or a column value that will be used as JSON values
        """
        return "json_group_object(%s, %s)" % (name, value)

    def build_limit(self):
        """
        Constructs the LIMIT expression

        :return: a string containing the limit expression
        """
        query = None
        if self._limit:
            query = "LIMIT %d OFFSET %d" % (self._limit, self._offset)
        return query
