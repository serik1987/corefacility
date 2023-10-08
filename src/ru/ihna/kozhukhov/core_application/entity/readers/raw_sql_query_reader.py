from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityNotFoundException
from .sql_query_reader import SqlQueryReader


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
            self.__execute_query(cursor, query)
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
            self.__execute_query(cursor, query)
            result_row = cursor.fetchone()
        if result_row is None:
            raise EntityNotFoundException()
        else:
            return self.create_external_object(*result_row)

    def __execute_query(self, cursor, query):
        """
        Executes a query build by the builder or prints it in case of fail

        :param cursor: the SQL cursor
        :param query: an output of the QueryBuilder's build() function (a tuple with a query itself and its arguments)
        :return: nothing
        """
        try:
            cursor.execute(query[0], query[1:])
        except (OperationalError, ProgrammingError) as e:
            print("======================== ERROR IN QUERY HAPPENED ===================================")
            print(self.items_builder)
            print("======================== END OF THE ERROR REPORT ===================================")
            raise e
