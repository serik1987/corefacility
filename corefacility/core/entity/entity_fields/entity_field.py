from core.entity.entity_exceptions import EntityFieldInvalid


class EntityField:
    """
    Defines the default entity field.

    The entity field is stored inside the Entity itself and contains rules how the user
    can read the field value of a certain entity and write some value to the same field.

    The EntityField can't be treated as validator. The goal of the EntityField is just
    guarantee that all information stored to all entity sources can be retrieved without
    being corrupted or refuse the user to do it if this is not possible
    """

    _default = None
    _value_class = None
    _min_length = None
    _max_length = None
    _min_value = None
    _max_value = None
    _description = None

    @staticmethod
    def identity(value):
        """
        See __init__ constructor description for details

        :param value: some value
        :return: the same value
        """
        return value

    def __init__(self, value_class, min_length=None, max_length=None, min_value=None, max_value=None, default=None,
                 description: str = None):
        """
        Initializes the EntityField. After being initialized the EntityField shall be added inside the
        '_public_field_description' dictionary inside the Entity object

        :param value_class: Before writing to the field this entity value will be cast to a type given in this argument.
            Use EntityField.identity if you don't want such a cast.
        :param min_length: next, if len(value) is less than the value of this parameter, EntityFieldInvalid will be
        thrown. Not applied if this parameter equals to None.
        :param max_length: if len(value) is greater than this value, EntityFieldInvalid will be thrown.
        Not applied if this parameter equals to None.
        :param min_value: if value itself is less than this value, EntityFieldInvalid will be thrown.
        Not applied if this parameter equals to None.
        :param max_value: if value itself is greater than this value, EntityFieldInvalid will be thrown.
        Not applied if this parameter equals to None.
        :param default: Entity default value. Such value will be assigned to 'creating' entity by default
        :param description: The entity string description used for logging and debugging
        """
        self._value_class = value_class
        self._min_length = min_length
        self._max_length = max_length
        self._min_value = min_value
        self._max_value = max_value
        self._default = default
        self._description = str(description)

    @property
    def default(self):
        """
        Returns the default value of this entity field.
        The default value will be assigned to the entity if the entity is newly created rather than loaded from the
        external source and such value is not passed through the default constructor

        :return: the default value of this entity.
        """
        return self._default

    @property
    def description(self):
        """
        Returns the entity description to use in logging and debugging

        :return: The entity description to use in logging and debugging
        """
        return self._description

    def proofread(self, value):
        """
        Proofreads the entity value. The method is called when the entity gets the field value to the user.
        Such value passes to the user itself who in turn proofreads such value

        :param value: the value stored in the entity as defined by one of the entity providers
        :return: the value given to the user
        """
        return value

    def correct(self, value):
        """
        Corrects the value before the user sets it to the entity field.

        :param value: the value that user wants to set
        :return: Actual value set to the entity
        """
        if value is None:
            raw_value = None
        else:
            raw_value = self._value_class(value)
        if raw_value is None:
            if self._min_length is not None and self._min_length > 0:
                raise EntityFieldInvalid("Entity")
        else:
            if self._min_length is not None and len(raw_value) < self._min_length:
                raise EntityFieldInvalid("Entity")
            if self._max_length is not None and len(raw_value) > self._max_length:
                raise EntityFieldInvalid("Entity")
            if self._min_value is not None and raw_value < self._min_value:
                raise EntityFieldInvalid("Entity")
            if self._max_value is not None and raw_value > self._max_value:
                raise EntityFieldInvalid("Entity")
        return raw_value
