from enum import Enum

from .base import QueryBuilder


class MysqlQueryBuilder(QueryBuilder):
    """
    Implements query builder for MySQL queries
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
        RIGHT = "RIGHT JOIN"
        CROSS = "CROSS JOIN"

    _nulls_direction_support = False

    def _build_select_expression(self, expr, alias, kwargs):
        if len(self._group_col) > 0:
            if "agg_safe_int" in kwargs and kwargs['agg_safe_int']:
                expr = "AVG(%s)" % expr
            elif "agg_safe_str" in kwargs and kwargs['aff_safe_str']:
                expr = "GROUP_CONCAT(%s)" % expr
        return super()._build_select_expression(expr, alias, kwargs)

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
