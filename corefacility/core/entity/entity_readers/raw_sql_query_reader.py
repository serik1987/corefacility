from django.db import connection

from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.entity_readers.sql_query_reader import SqlQueryReader


class RawSqlQueryReader(SqlQueryReader):
    """
    The raw SQL query reader doesn't need any Django model. It interacts directly with the SQL backend
    both during the construction and sending SQL queries and during interpretation of SQL results.
    """

    def create_external_object(self, *args):
        """
        Transforms the query result row into any external object that is able to read by the entity reader

        :param args: cell values from the result row
        :return: an external object
        """
        raise NotImplementedError("Please, implement the create_external_object")

    def pick_many_items(self):
        """
        Executes the query containing in the items builder and returns the result containing
        several items.

        :return: an iterator or iterable object containing many, 1 or even zero external objects
        (the external object is any object that makes entity provider's wrap_entity method working
        correctly. Django model as well as python's dict is OK)
        """
        if self._query_debug:
            print(self.items_builder)
        query = self.items_builder.build()
        with connection.cursor() as cursor:
            cursor.execute(query[0], query[1:])
            while True:
                result_row = cursor.fetchone()
                if result_row is None:
                    break
                yield self.create_external_object(*result_row)

    def pick_one_item(self):
        """
        Executes the query containing in the item builder and returns the result
        containing one item.

        :return: single external object
        (the external object is any object that makes entity provider's wrap_entity method working
        correctly. Django model as well as python's dict is OK)
        """
        if self._query_debug:
            print(self.items_builder)
        query = self.items_builder.build()
        with connection.cursor() as cursor:
            cursor.execute(query[0], query[1:])
            result_row = cursor.fetchone()
        if result_row is None:
            raise EntityNotFoundException()
        else:
            return self.create_external_object(*result_row)
