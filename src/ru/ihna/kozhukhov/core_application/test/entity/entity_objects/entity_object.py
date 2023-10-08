class EntityObject:
    """
    An auxiliary object that facilitates entity testing and makes the testing code more attractive

    The entity object contains entity inside it
    """

    _entity = None
    """ The entity inside the project """

    _entity_class = None
    """ The entity class that is used to create the entity itself """

    _default_create_kwargs = {}
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {}
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """

    _entity_fields = None
    """
    The entity fields. When some values were assigned to the entity fields their copy will be assigned here.
    Next, when the entity is loaded these fields will be checked
    """

    _id = None
    """
    The entity ID. When the entity is created the id is assigned to this field. When the entity object is created you
    can put the entity ID to the keyword arguments.
    """

    @classmethod
    def get_entity_class(cls):
        """
        Returns the entity class. When creating the entity this class will be used as base class

        :return: the entity class
        """
        if cls._entity_class is None:
            raise NotImplementedError("Please, define the _entity_class class field when extending the EntityObject")
        else:
            return cls._entity_class

    @classmethod
    def define_default_kwarg(cls, name, value):
        """
        If some default entity fields must be defined during the setup or tear down please, use this method
        to do it

        :param name: the default field name
        :param value: the default field value
        :return: nothing
        """
        cls._default_create_kwargs[name] = value

    @classmethod
    def define_change_kwarg(cls, name, value):
        """
        If some default change fields must be defined during the setup or tear down, please, use this method to do it

        :param name: the field name
        :param value: the field value
        :return: nothing
        """
        cls._default_change_kwargs[name] = value

    def __init__(self, use_defaults=True, **kwargs):
        """
        Creates the entity object that results to creating an entity

        :param use_defaults: if True, the constructor will use the _default_create_kwargs fields. Otherwise this
        class property will be ignored
        :param kwargs: Any additional field values that shall be embedded to the entity or 'id' that reflects the
        entity ID
        """
        if 'id' in kwargs:
            self._id = int(kwargs['id'])
            del kwargs['id']
        if use_defaults:
            options = self._default_create_kwargs.copy()
            options.update(kwargs)
        else:
            options = kwargs
        self._entity = self.get_entity_class()(**options)
        self._entity_fields = options

    @property
    def entity(self):
        """
        The entity that this entity object works on

        :return: the entity that this entity object works on
        """
        return self._entity

    @property
    def entity_fields(self):
        """
        The entity fields. When some values were assigned to the entity fields their copy will be assigned here.
        Next, when the entity is loaded these fields will be checked
        """
        return self._entity_fields

    @property
    def id(self):
        """
        When the entity is 'CREATING' this field value is None. Otherwise this field value is ID of the entity recently
        created

        :return: The entity ID
        """
        return self._id

    @property
    def default_field_key(self):
        """
        Returns keys from all default keyword args, just for additional checks

        :return:
        """
        return self._default_create_kwargs.keys()

    @property
    def changed_field_key(self):
        """
        Returns keys from all fields that were recently changed

        :return:
        """
        return self._default_change_kwargs.keys()

    def create_entity(self):
        """
        Creates an entity wrapped to this entity object and stores the entity to the database.
        The 'id' property will be updated according to the entity status

        :return: the entity created
        """
        self._entity.create()
        self._id = self._entity.id

    def change_entity_fields(self, use_defaults=True, **kwargs):
        """
        Changes some fields of the wrapped entity

        :param use_defaults: if True the _default_change_kwargs property will be applied. If false, nothing will be
        applied
        :param kwargs: additional entity fields to change. All kwargs defined here will override the default kwargs
        :return: nothing
        """
        if use_defaults:
            options = self._default_change_kwargs.copy()
            options.update(kwargs)
        else:
            options = kwargs
        for name, value in options.items():
            setattr(self._entity, name, value)
            self._entity_fields[name] = value

    def reload_entity(self):
        """
        Loads the recently saved entity from the database

        :return: nothing
        """
        if self._id is None:
            raise RuntimeError("EntityObject.reload_entity: can't reload the entity that is recently saved")
        entity_set = self._entity.get_entity_set_class()()
        self._entity = entity_set.get(self._id)
