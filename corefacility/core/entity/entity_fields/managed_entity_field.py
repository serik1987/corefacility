from .read_only_field import ReadOnlyField
from .entity_value_manager import EntityValueManager


class ManagedEntityField(ReadOnlyField):
    """
    The 'managed entity field' is a field that provides indirect access to user through so called
    'entity field manager'.

    This means that when the user try to read the field he receives the EntityValueManager instance that allows
    him to indirectly access the field. The field writing access will cause error
    """

    _field_manager_class = None

    def __init__(self, field_manager_class, description=None, default=None):
        """
        Initializes the managed entity field

        :param field_manager_class: the field manager class.
        :param description: the field description as usual
        :param default: the default value that have to be used internally by the manager
        """
        super().__init__(description=description, default=default)
        self._field_manager_class = field_manager_class

    def proofread(self, value) -> EntityValueManager:
        """
        Provides the indirect reading access to that entity field

        :param value: the field values stored inside the entity
        :return: the field value manager that the user can use
        """
        return self._field_manager_class(value, self._default)

    @property
    def default(self):
        """
        Returns the default property value

        :return: the default property value and the manager that allows to manage this
        """
        return self._field_manager_class(None, self._default)
