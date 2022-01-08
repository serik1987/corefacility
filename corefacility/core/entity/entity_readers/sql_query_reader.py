from django.conf import settings
from django.db import connection


from .entity_reader import EntityReader
from .query_builders.query_filters import StringQueryFilter, AndQueryFilter
from ..entity_exceptions import EntityNotFoundException


class SqlQueryReader(EntityReader):
    """
    This is the base class for RawSqlReader and RawSqlModelReader that implements reader interactions with the
    query sets.

    When deriving from this class, don't forget to implement apply_***_filter where *** is filter name.
    If you don't do this the user will get AttributeError when trying to apply a certain filter.
    """

    __items_builder = None
    __count_builder = None

    _query_debug = False
    """ Set this class property to True if you want to print your SQL query on the screen """

    _lookup_table_name = None
    """
    Change this property if get() method will give you something like 'column ... is ambiguous'.
    This will make get() method to add 'WHERE tbl_name.id=%s' instead of 'WHERE id=%s'
    """

    def __init__(self, **kwargs):
        """
        Initializes the SQL query reader

        :param kwargs: some filter kwargs
        """
        self.__items_builder = settings.QUERY_BUILDER_CLASS()\
            .set_main_filter(AndQueryFilter())
        self.__count_builder = settings.QUERY_BUILDER_CLASS()\
            .set_main_filter(AndQueryFilter())
        self.initialize_query_builder()
        for name, value in kwargs.items():
            getattr(self, "apply_%s_filter" % name)(value)

    @property
    def items_builder(self):
        """
        The items builder is used for query iteration slicing, indexation, reading entities by ID and alias

        :return: the items builder
        """
        return self.__items_builder

    @property
    def count_builder(self):
        """
        The count builder is used for revealing length of the query sets

        :return: the count builder
        """
        return self.__count_builder

    def initialize_query_builder(self):
        """
        This function shall call certain methods for the query builder to make
        it to generate proper queries given that no external filters applied

        :return: nothing
        """
        raise NotImplementedError("the method must be implemented")

    def pick_many_items(self):
        """
        Executes the query containing in the items builder and returns the result containing
        several items.

        :return: an iterator or iterable object containing many, 1 or even zero external objects
        (the external object is any object that makes entity provider's wrap_entity method working
        correctly. Django model as well as python's dict is OK)
        """
        raise NotImplementedError("the pick_many_items method is not implemented")

    def pick_one_item(self):
        """
        Executes the query containing in the item builder and returns the result
        containing one item.

        :return: single external object
        (the external object is any object that makes entity provider's wrap_entity method working
        correctly. Django model as well as python's dict is OK)
        """
        raise NotImplementedError("The pick_one_item method is not implemented")

    def __iter__(self):
        """
        The method is called by the EntitySet's __iter__ method and must return iterator
        that allows to consecutively read all entities from the external source.

        The function is responsible for reading the entity information and for wrapping it by the entity
        filter.

        :return: the iterator of Entity objects
        """
        for external_object in self.pick_many_items():
            yield external_object

    def __getitem__(self, index):
        """
        The method is called by the EntitySet's __getitem__ method and must return:

        - a single entity if index is integer
        - a list or any other iterable entity container if index is slice.

        The main goal of this method is to retrieve such entities from the external source
        which indices satisfy the 'index' condition.

        Note that negative slicing is not supported by this entity reader and all its subclasses.

        :param index: either integer or slice instance
        :return: see above
        """
        if isinstance(index, int):
            self.items_builder.limit(index, 1)
            return self.pick_one_item()
        elif isinstance(index, slice):
            istart = index.start if index.start is not None else 0
            istep = index.step if index.step is not None else 1
            istop = index.stop
            if istart < 0 or istep != 1:
                raise EntityNotFoundException()
            elif istop is not None and istart >= istop:
                external_object_collection = list()
            else:
                icount = istop - istart if istop is not None else None
                self.items_builder.limit(istart, icount)
                external_object_collection = self.pick_many_items()
            return external_object_collection
        else:
            raise ValueError("The Entity provider provides indexation by positive integers os slices only")

    def get(self, **kwargs):
        """
        Looks for a single entity in the entity source. If entity exists it returns the entity
        itself. If entity doesn't exist, it shall throw the following exception:
        core.entity.entity_exceptions.EntityNotFoundException

        :param kwargs: They depend on how the entity_set is used
        entity_set.get(ID) will call entity_reader.get(id=ID)
        entity_set.get("some_alias") will call entity_reader.get(alias="some_alias")
        :return: a single Entity object
        """
        for filter_name, filter_value in kwargs.items():
            if self._lookup_table_name is None:
                lookup_filter_clause = "%s=%%s" % filter_name
            else:
                lookup_filter_clause = "%s.%s=%%s" % (self._lookup_table_name, filter_name)
            self.items_builder.main_filter &= StringQueryFilter(lookup_filter_clause, filter_value)
        return self.pick_one_item()

    def __len__(self):
        """
        Returns total number of entities that can be read by this reader given all reader filters were applied.

        The entity length must be retrieved using SELECT COUNT(*) query type

        :return: total number of entities that can be read
        """
        if self._query_debug:
            print(self.count_builder)
        query = self.count_builder.build()
        with connection.cursor() as cursor:
            cursor.execute(query[0], query[1:])
            result_set = cursor.fetchone()
        return result_set[0]
