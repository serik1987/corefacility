from django.db.models import QuerySet
from django.utils.module_loading import import_string

from .entity_reader import EntityReader
from ..entity_exceptions import EntityNotFoundException


class ModelReader(EntityReader):
    """
    Implements the entity reader based on reading from the Django model
    """

    _entity_model_class = None
    """ The entity model that is used for seeking a proper entity data """

    __entity_data = None
    """ The QuerySet that corresponds to all entity data found """

    _filter_map = {}
    """
    Establishes the correspondence between EntitySet filter name and Django model manager filter name
    All EntitySet filters that were present in this maps will be substituted to the Django model manager filter
    names related to corresponding values.
    If the EntitySet filter is absent here this mean that both filter names were the same.
    """

    def __init__(self, **kwargs):
        """
        Initializes the model reader

        :param kwargs: filter keyword arguments
        """
        self.__entity_data = self.entity_model_class.objects
        for name, value in kwargs.items():
            if name in self._filter_map:
                name = self._filter_map[name]
            self.__entity_data = self.__entity_data.filter(**{name: value})

    @property
    def entity_model_class(self):
        """
        The entity model that is used for seeking a proper entity data
        """
        if self._entity_model_class is None:
            raise NotImplementedError("ModelReader._entity_model_class: this class property must be defined")
        if isinstance(self._entity_model_class, str):
            self._entity_model_class = import_string(self._entity_model_class)
        return self._entity_model_class

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
        try:
            return self.__entity_data.get(**kwargs)
        except self.get_entity_provider().entity_model.DoesNotExist:
            raise EntityNotFoundException()

    def __iter__(self):
        """
        The method is called by the EntitySet's __iter__ method and must return iterator
        that allows to consecutively read all entities from the external source.

        The function is responsible for reading the entity information and for wrapping it by the entity
        filter

        :return: the iterator of Entity objects
        """
        if not isinstance(self.__entity_data, QuerySet):
            self.__entity_data = self.__entity_data.all()
        for external_object in self.__entity_data:
            yield external_object

    def __getitem__(self, index):
        """
        The method is called by the EntitySet's __getitem__ method and must return:

        - a single entity if index is integer
        - a list or any other iterable entity container if index is slice.

        The main goal of this method is to retrieve such entities from the external source
        which indices satisfy the 'index' condition

        :param index: either integer or slice instance
        :return: see above
        """
        if not isinstance(self.__entity_data, QuerySet):
            self.__entity_data = self.__entity_data.all()
        try:
            return self.__entity_data[index]
        except (AssertionError, IndexError):
            raise EntityNotFoundException()

    def __len__(self):
        """
        Returns total number of entities that can be read by this reader given all reader filters were applied.

        The entity length will be retrieved using SELECT COUNT(*) query type

        :return: total number of entities that can be read
        """
        return self.__entity_data.count()
