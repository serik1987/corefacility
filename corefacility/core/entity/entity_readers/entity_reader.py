class EntityReader:
    """
    The EntityReader is an object that is responsible for looking
    for an appropriate entity from the external source.

    Mainly, the EntityReader instance is created when you try
    to use EntitySet by means of iteration or slicing facilities or
    by using 'get' method. Then, it searches the information on
    external entity source. Once such information has been found,
    the EntityReader transforms this information to a sequence of
    Entity objects and return the list/iterator of such objects.

    Particularly, the function of the entity reader:

    1. Creates an object responsible for the information search
    on the external data source (django.db.models.Manager instance is OK,
    Django database QuerySet is also OK).

    2. Copies all filters from the EntitySet object to this external object.
    The EntitySet is the only object that will create instances of this object
    and it passes all the filters to the object constructor. By default,
    object constructor applies the 'apply_my_filter' function.

    Example, if the EntitySet calls the EntityReader using the following constructor:

    reader = EntityReader(is_locked=False, activation_code_not_expired=True)

    the EntityReader constructor will call two following methods:
    reader.apply_is_locked_filter(obj, False)
    reader.apply_activation_code_not_expired_filter(obj, True)

    This is your responsibility to add such methods

    3. Retrieves the list of all objects that met the satisfied condition

    4. Fully destroys discarding all the filters applied

    The cycle length is a single EntitySet's __iter__, __getitem__ or get method.
    The EntityReader does not exist between calls of all these methods.

    """

    _entity_provider = None
    """
    The instance of the entity provider. When the EntityReader finds an information about
    the entity from the external source that satisfies filter conditions, it calls the
    wrap_entity method of the _entity_provider given here
    """

    @classmethod
    def get_entity_provider(cls):
        if cls._entity_provider is None:
            raise NotImplementedError("EntityReader.get_entity_provider: Either define the entity provider "
                                      "class or re-implement the get_entity_provider method")
        else:
            return cls._entity_provider

    def __init__(self, **kwargs):
        """
        Creates the EntityReader instance

        :param kwargs: all filter values that will be transmitted from the EntitySet to the external object
        responsible for the filter lookup
        """
        raise NotImplementedError("EntityReader.__init__ the method is not implemented. Hence, the EntityReader "
                                  "class is purely abstract: no any instance can be created")

    def __iter__(self):
        """
        The method is called by the EntitySet's __iter__ method and must return iterator
        that allows to consecutively read all entities from the external source.

        The function is responsible for reading the entity information and for wrapping it by the entity
        filter

        :return: the iterator of Entity objects
        """
        raise NotImplementedError("EntityReader.__iter__: the method is not implemented")

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
        raise NotImplementedError("EntityReader.__getitem__: the method is not implemented")

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
        raise NotImplementedError("EntityReader.get: the method is not implemented")
