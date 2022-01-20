from datetime import datetime
from django.utils.timezone import make_aware

from core.entity.entity_exceptions import EntityFieldInvalid

from .entity_value_manager import EntityValueManager


class CurrentTimeManager(EntityValueManager):
    """
    Defines the current time with restricted writing capabilities
    """

    def mark(self):
        """
        Sets time to the current one if and only if it has not already been set.

        :return: nothing
        """
        if self._field_value is None:
            setattr(self.entity, '_' + self.field_name, make_aware(datetime.now()))
            self.entity.notify_field_changed(self.field_name)
        else:
            raise EntityFieldInvalid(self.field_name)

    def get(self):
        """
        Returns the log creation date as datetime object

        :return: the log creation date
        """
        return self._field_value

    def __str__(self):
        return str(self.get())

    def __repr__(self):
        return str(self.get())

    def __eq__(self, other):
        if isinstance(other, CurrentTimeManager):
            return self.get() == other.get()
        else:
            return False
