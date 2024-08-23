from datetime import datetime

from django.utils.timezone import is_naive, make_aware, make_naive, is_aware

from .entity_field import EntityField
from ...exceptions.entity_exceptions import EntityFieldInvalid


class DateTimeField(EntityField):
    """
    Represents date and time
    """

    def __init__(self, default=None, description: str = None):
        """
        Initializes the field

        :param default: the default value
        :description: Human-readable description
        """
        super().__init__(self.identity, default=default, description=description)

    def proofread(self, value):
        """
        Proofreads the entity value. The method is called when the entity gets the field value to the user.
        Such value passes to the user itself who in turn proofreads such value

        :param value: the value stored in the entity as defined by one of the entity providers
        :return: the value given to the user
        """
        if value is not None and is_aware(value):
            value = make_naive(value)
        return value

    def correct(self, value):
        """
        Checks the value before its store to the database
        """
        if value is None:
            raw_value = None
        elif isinstance(value, datetime):
            raw_value = value
        else:
            raise EntityFieldInvalid("The value must be an instance of datetime")
        if raw_value is not None and is_naive(raw_value):
            raw_value = make_aware(raw_value)
        return raw_value


class DateTimeReadOnlyField(DateTimeField):
    """
    Represents date and time for the read-only purpose
    """

    def correct(self, value):
        """
        Checks the value before its store to the database
        """
        raise ValueError("This field is read-only")
