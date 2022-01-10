from core.entity.entity_exceptions import EntityNotFoundException


class EntitySetObject:
    """
    The EntitySetObject is a simple immitation of the entity set that allows to generate expected
    results among search within the entity set itself. Such results must be coincided with another
    ones retrieved from entities.

    When you create a proper EntitySetObject the entities will be added to the entity sets automatically.
    """

    _entities = None
    """ Declares the list of all entities in the set """

    _entity_class = None
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    _alias_field = "alias"
    """ The alias field. Override this class property is this is not true. """

    def __init__(self, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param _entity_list: This is an internal argument. Don't use it.
        """
        if _entity_list is not None:
            self._entities = _entity_list
        else:
            self._entities = []
            for entity_fields in self.data_provider():
                entity = self.entity_class(**entity_fields)
                entity.create()
                self._entities.append(entity)

    @property
    def entity_class(self):
        if self._entity_class is None:
            raise NotImplementedError("EntitySetObject._entity_class was not defined")
        else:
            return self._entity_class

    @property
    def entities(self):
        """
        List of all entities in the entity set object
        """
        return self._entities

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        raise NotImplementedError("EntitySetObject.data_provider: the function was not implemented")

    def __len__(self):
        """
        Returns total number of entities containing in this entity set

        :return: total number of entities containing in this entity set
        """
        return len(self._entities)

    def __getitem__(self, item):
        """
        Returns an item with a given index

        :param item: the item index or item slice
        :return: entity is item index is given or list of items if item slice is given
        """
        return self._entities[item]

    def get_by_id(self, id):
        """
        Returns the entity from the set using the entity ID

        :param id: the entity ID
        :return: entity itself
        """
        for entity in self._entities:
            if entity.id == id:
                return entity
        raise EntityNotFoundException()

    def get_by_alias(self, alias):
        """
        Returns an entity with a certain alias

        :param alias: the alias to find
        :return: entity itself
        """
        for entity in self._entities:
            if getattr(entity, self._alias_field) == alias:
                return entity
        raise EntityNotFoundException()

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(_entity_list=list(self._entities))

    def print_entities(self):
        """
        Prints all entities (for debugging purpose)

        :return: nothing
        """
        for entity in self._entities:
            print(entity)
