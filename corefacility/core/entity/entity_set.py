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
    """ Defines the entity class """

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

    @classmethod
    def get_entity_class(cls):
        """
        Defines the entity class. The entity class is important to move from the entity set
        to the entity

        :return: A subclass of the Entity class
        """
        if cls._entity_class is not None:
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
        raise NotImplementedError("TO-DO: EntitySet.get")

    def __getitem__(self, index):
        """
        The EntitySet supports slicing in the following way:
        entity_set[7] returns the 7th entity in the set
        entity_set[3:8] returns from 3rd till 8th entity in the set
        entity_set[3:8:2] returns every odd entity from the set from 3rd till 8th

        :param index: either integer or a slice instance
        :return: if index is integer the method returns a single Entity object. If index is slice
        the method returns the entity list or any other iterable container of the entities
        """
        raise NotImplementedError("TO-DO: EntitySet.__getitem__")

    def __iter__(self):
        """
        The EntitySet supports iteration that allows to sequentially process each entity from the set
        """
        raise NotImplementedError("TO-DO: EntitySet.__iter__")
