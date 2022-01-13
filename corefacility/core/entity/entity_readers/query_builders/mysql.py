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

    def add_select_expression(self, expr, alias=None, **kwargs):
        """
        Adds the select expression (a term between SELECT and FROM keywords).
        Don't afraid to use build-in select_**** since they provide platform independent selection routines.
        They are always either static or class methods

        :param expr: expression to select
        :param alias: resultant column name
        :param kwargs: any platform-dependent options that will be ignored on the other platforms. Any platform
        supports the following options:
            agg_safe_int - if column contains integers, you use GROUP BY condition group results you may reveal an
            error 'SELECT list is not in GROUP BY clause and contains non-aggregated column'. If you do this,
            put agg_safe_int=True to overcome the problem. This will wrap the column by proper aggregate function
            agg_safe_str - if column contains strings, you use GROUP BY condition group results you may reveal an
            error 'SELECT list is not in GROUP BY clause and contains non-aggregated column'. If you do this,
            put agg_safe_int=True to overcome the problem. This will wrap the column by proper aggregate function
        :return: nothing
        """
        if "agg_safe_int" in kwargs and kwargs['agg_safe_int']:
            expr = "AVG(%s)" % expr
        elif "agg_safe_str" in kwargs and kwargs['agg_safe_str']:
            expr = "GROUP_CONCAT(%s)" % expr
        return super().add_select_expression(expr, alias, **kwargs)

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
