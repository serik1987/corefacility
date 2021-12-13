class EntityValueManager:
    """
    When the entity field allows only indirect access to its value the EntityValueManager is someone who organizes
    such indirect access.

    Each indirect access of the field is fully completed: the data must be saved without additional call of create()
    and save() method
    """

    _entity = None
    """ The entity which value shall be managed """

    _field_name = None
    """ Name of the field within this entity (don't forget to add underscore _ during the indirect access) """

    _field_value = None
    """ Current field value set up by the user or previously stored in the database """

    _default_value = None
    """ The default value shown by the manager when no field value was stored in the entity """

    def __init__(self, value, default_value=None):
        """
        Initializes the entity manager

        :param value: the entity value as it was stored inside the entity. For newly created entity value is always
        None
        :param default_value: some default value that the manager shows when there is no actual value stored in the
        entity
        """
        self._field_value = value
        self._default_value = default_value

    @property
    def entity(self):
        """
        The entity which value shall be managed.
        """
        return self._entity

    @entity.setter
    def entity(self, value):
        self._entity = value

    @property
    def field_name(self):
        """
        The field name inside the entity
        """
        return self._field_name

    @field_name.setter
    def field_name(self, value):
        self._field_name = value
