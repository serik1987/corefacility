from django.utils.module_loading import import_string
from .entity_field import EntityField


class RelatedEntityField(EntityField):
    """
    Defines the entity field which value is some entity connected with a given entity using "one-to-many"
    relationships
    """

    _entity_class = None

    def __init__(self, entity_class: str, description=None):
        """
        Constructs the related entity field

        :param entity_class: the entity class used for the construction
        :param description: the field description used for logging or debugging purpose
        """
        super().__init__(EntityField.identity, description=description)
        self._entity_class = entity_class

    def correct(self, value):
        """
        Corrects the related entity field when the user assigns its value to an object

        :param value: the field value the user wants to assign
        :return: the field value that will actually be assigned
        """
        if isinstance(self._entity_class, str):
            self._entity_class = import_string(self._entity_class)
        if not isinstance(value, self._entity_class):
            raise ValueError("RelatedEntityField.correct: attempting to assign the incorrect entity type")
        if value.state == "creating" or value.state == "deleted":
            raise ValueError("RelatedEntityField.correct: the value is not create()'d before assigning")
        return value
