from .sql_query_reader import SqlQueryReader
from ..entity_exceptions import EntityNotFoundException


class SqlModelReader(SqlQueryReader):
    """
    Defines the reader based on execution of the raw SQL queries which results can be interpreted in terms
    of Django model.

    The query were executed by means of model manager facilities and query results will be automatically
    converted to Django models. So, you shall worry about query making but you shall not worry about their
    interpretation
    """

    _entity_model_class = None
    """ The entity model that is used for seeking a proper entity data """

    @property
    def entity_model_class(self):
        """
        The entity model that is used for seeking a proper entity data
        """
        if self._entity_model_class is None:
            raise NotImplementedError("ModelReader._entity_model_class: this class property must be defined")
        return self._entity_model_class

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
        build_result = self.items_builder.build()
        return self.entity_model_class.objects.raw(build_result[0], build_result[1:])

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
        try:
            build_result = self.items_builder.build()
            external_object = self.entity_model_class.objects.raw(build_result[0], build_result[1:])[0]
        except IndexError:
            raise EntityNotFoundException()
        return external_object
