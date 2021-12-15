from datetime import timedelta, datetime
from .entity_value_manager import EntityValueManager


class ExpiryDateManager(EntityValueManager):
    """
    Manages the value connected with so called "expiration date"

    The manager can be used to restrict the access to the 'expiration date' field
    """

    def set(self, interval: timedelta):
        """
        Sets the expiration date. The expiration data will be calculated automatically
        based on the interval given by the user.

        Does not save the object to the database

        :param interval: how much time shall it take from the last expiration in order to
        treat some data as 'expired'. Must be an instance of datetime.timedelta
        :return: Nothing
        """
        value = datetime.now() + interval
        setattr(self.entity, "_" + self.field_name, value)
        self.entity.notify_field_changed(self.field_name)

    def is_expired(self):
        """
        Returns True is the the data is expired, False otherwise.

        If the expiry date is not defined the function always returns False due to security considerations

        :return: True if the data is expired, False otherwise
        """
        if self._field_value is None:
            return False
        cdate = datetime.now()
        return cdate > self._field_value

    def clear(self):
        """
        Clears the expiry date.

        Does not save the object to the database.

        :return: nothing
        """
        setattr(self.entity, "_" + self.field_name, None)
        self.entity.notify_field_changed(self.field_name)

    def clear_all(self):
        """
        Clears all object instances where this field is expired given that
        database data provider is the only data provider here.

        Produces one single SQL query to delete all expired objects from the database

        :return: nothing
        """
        raise NotImplementedError("TO-DO: EntityDateManager.clear_all")

    def __repr__(self):
        """
        Returns a concise representation of the expiry date field

        :return: a concise representation of the expiry date field
        """
        return str(self._field_value)
