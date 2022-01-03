from django.db.models import QuerySet
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
        for name, value in kwargs:
            if name in self._filter_map:
                name = self._filter_map[name]
            self.__entity_data = self.__entity_data.filter(**{name: value})

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

    @property
    def entity_model_class(self):
        """
        The entity model that is used for seeking a proper entity data
        """
        if self._entity_model_class is None:
            raise NotImplementedError("ModelReader._entity_model_class: this class property must be defined")
        return self._entity_model_class
