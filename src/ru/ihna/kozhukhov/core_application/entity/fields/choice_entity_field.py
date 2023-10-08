from django.utils.module_loading import import_string

from .entity_field import EntityField


class ChoiceEntityField(EntityField):
    """
    A choice field can accept only several string values
    """

    _choice_class = None

    def __init__(self, choice_class, description=None):
        """
        Initializes the choice field

        :param choice_class: a choice class (a subclass of the django.db.models.TextChoices)
        :param description: a field description
        """
        super().__init__(str, description=description)
        self._choice_class = choice_class

    def correct(self, value):
        raw_value = super().correct(value)
        if isinstance(self._choice_class, str):
            self._choice_class = import_string(self._choice_class)
        raw_value = self._choice_class(raw_value)
        return raw_value
