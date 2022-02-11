from django.db.models import QuerySet
from django.utils.module_loading import import_string

from core.entity.entity_exceptions import EntityNotFoundException, EntityOperationNotPermitted
from ..entity_providers.entity_provider import EntityProvider


class EntitySet:
    """
    The entity set can be treated as container for entities.

    The goal of the EntitySet is:

     (a) to provide unified and simplified access to the object lists waiving a final user from writing and profiling
     numerous applications of filters and many other properties of the Manager instance

     (b) to optimize the database reading procedure

    Despite the Entity object that deals with different information sources the EntitySet
    works solely with the database
    """

    _entity_name = None
    """ A human-readable entity name used for logging """

    _entity_class = None
    """ Defines the entity class. Pass string value to this field to prevent circular import """

    _entity_reader_class = None
    """
    Defines the entity reader class. The EntitySet interacts with external data source through the entity
    readers.
    """

    _entity_filters = None
    """
    The list of entity filters. Each entity filter is set by the user through setting a certain entity property.
    The goal of the entity filter setter is update this dictionary
    """

    _entity_filter_list = {}
    """
    Defines the entity filter list. The values are represented in the following form:
        'filter_name': [filter_type, additional_validator]
    
    Additional filter validator is a function that takes the filter value entered by the user and returns another
    value. Use no if you don't want any additional filter validation
    """

    _alias_kwarg = "alias"
    """ Defines the name of the field in Django model that is used for alias lookup by get('some_alias_string') """

    @classmethod
    def get_entity_class(cls):
        """
        Defines the entity class. The entity class is important to move from the entity set
        to the entity

        :return: A subclass of the Entity class
        """
        if cls._entity_class is not None:
            if isinstance(cls._entity_class, str):
                cls._entity_class = import_string(cls._entity_class)
            return cls._entity_class
        else:
            raise NotImplementedError("You must implement the get_entity_class() class method or change the "
                                      "value of the _entity_class class property")

    @classmethod
    def get_entity_name(cls):
        """
        Defines the human-readable entity name. This name will be used to create logs

        :return: the entity name (string)
        """
        if cls._entity_name is not None:
            return cls._entity_name
        else:
            raise NotImplementedError("You must implement the get_entity_name() class method or change the "
                                      "value of the _entity_name class property")

    def __init__(self):
        """
        Initializes the entity set
        """
        self._entity_filters = dict()

    @property
    def entity_reader_class(self):
        if self._entity_reader_class is None:
            raise NotImplementedError("Define EntitySet._entity_reader_class")
        else:
            if isinstance(self._entity_reader_class, str):
                self._entity_reader_class = import_string(self._entity_reader_class)
            return self._entity_reader_class

    def get(self, lookup):
        """
        Finds the entity by id or alias
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity alias is a unique string name assigned by the user during the entity post.

        The function must be executed in one request

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        reader = self.entity_reader_class(**self._entity_filters)
        if isinstance(lookup, int):
            source = reader.get(id=lookup)
        elif isinstance(lookup, str):
            source = reader.get(**{self._alias_kwarg: lookup})
        else:
            raise ValueError("EntitySet.get: invalid lookup argument")
        provider = reader.get_entity_provider()
        return provider.wrap_entity(source)

    def __getitem__(self, index):
        """
        The EntitySet supports slicing in the following way:
        entity_set[7] returns the 7th entity in the set
        entity_set[3:8] returns from 3rd till 8th entity in the set

        However, the following slicing is not supported:
        - slicing with arbitrary step;
        - slicing where either start or stop index is negative;
        - slicing where start but not stop index is defined.

        The main goal for slicing entity sets is to send SQL queries containing LIMIT clause. Hence, the main
        slice functionality is restricted by condition related to this particular slice. Use the following notation
        to overcome such restriction:

        entity_set[:][3:]

        :param index: either integer or a slice instance
        :return: if index is an integer the method returns a single Entity object. If index is a slice
        the method returns python's list of all found entities (both for 0, 1 and many found entities)
        """
        reader = self.entity_reader_class(**self._entity_filters)
        provider = reader.get_entity_provider()
        if isinstance(index, slice):
            if index.step != 1 and index.step is not None:
                raise EntityOperationNotPermitted(
                    "The slicing operation with steps not equal to 1 is not supported on entity sets")
            if (index.start is not None and index.start < 0) or (index.stop is not None and index.stop < 0):
                raise EntityOperationNotPermitted("Negative indices are not supported for the entity set slicing")
            if index.start is not None and index.stop is None:
                raise EntityOperationNotPermitted("The stop index is None while the start index is not None")
            raw_dataset = reader[index]
            final_dataset = []
            for external_object in raw_dataset:
                entity = provider.wrap_entity(external_object)
                final_dataset.append(entity)
            return final_dataset
        else:
            return provider.wrap_entity(reader[index])

    def __iter__(self):
        """
        The EntitySet supports iteration that allows to sequentially process each entity from the set
        """
        reader = self.entity_reader_class(**self._entity_filters)
        provider = reader.get_entity_provider()
        for external_object in reader:
            entity = provider.wrap_entity(external_object)
            yield entity

    def __len__(self):
        """
        Returns total number of items satisfying item condition

        :return: number of items in the entity set
        """
        reader = self.entity_reader_class(**self._entity_filters)
        return len(reader)

    def __getattr__(self, name):
        """
        Returns the current filter value or None if the filter has not been set

        :param name: the filter name
        :return: the filter value
        """
        return self._entity_filters[name]

    def __setattr__(self, name, value):
        """
        Sets an appropriate filter value. None values and empty strings imply filter switch off

        :param name: filter name to set
        :param value: filter value
        :return: nothing
        """
        if name in self._entity_filter_list:
            if value == "" or value is None:
                delattr(self, name)
                return
            filter_type, filter_constraint = self._entity_filter_list[name]
            if isinstance(filter_type, str):
                filter_type = import_string(filter_type)
            if not isinstance(value, filter_type):
                raise ValueError("EntitySet: type of the filter '%s' is not valid" % name)
            if filter_constraint is not None and not filter_constraint(value):
                raise ValueError("EntitySet: constraint for '%s' filter fails" % filter_constraint)
            self._entity_filters[name] = value
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name):
        """
        Removes the filter from the filter list

        :param name: the filter name
        :return: nothing
        """
        try:
            del self._entity_filters[name]
        except KeyError:
            pass
