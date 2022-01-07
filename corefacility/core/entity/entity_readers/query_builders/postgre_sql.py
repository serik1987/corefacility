from .base import QueryBuilder


class PostgreSqlQueryBuilder(QueryBuilder):
    """
    Implements query builder for the Postgre SQL
    """

    def distinct(self, expression=None):
        """
        tells SQL engine to retrieve DISTINCT rows only (see DISTINCT keyword for your SQL query documentation)

        :param expression: when this is not None, PostgreSQL query builder will add ON clause after the DISTINCT
        keyword while other
        :return: self
        """
        self._distinct = True
        if expression is not None:
            self._distinct_expression = expression
        return self

    def build_distinct_conditions(self):
        """
        Constructs the distinct conditions if necessary.

        :return: query fragment
        """
        query = super().build_distinct_conditions()
        if self._is_distinct and self._distinct_expression is not None:
            query += " ON " + self._distinct_expression
        return query

    @classmethod
    def select_string_concatenation(cls, *args):
        """
        Returns an SQL query expression that concatenates different strings

        :param args: strings to concatenate (all are SQL expressions)
        :return: SQL query fragment for string concatenation
        """
        return " || ".join(args)

    def build_limit(self):
        """
        Constructs the LIMIT expression

        :return: a string containing the limit expression
        """
        query = None
        if self._limit:
            query = "LIMIT %d OFFSET %d" % (self._limit, self._offset)
        return query
