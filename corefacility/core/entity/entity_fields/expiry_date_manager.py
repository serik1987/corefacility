from datetime import timedelta
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
        raise NotImplementedError("TO-DO: ExpiryDateManager.set")

    def is_expired(self):
        """
        Returns True is the the data is expired, False otherwise.

        :return: True if the data is expired, False otherwise
        """
        raise NotImplementedError("TO-DO: ExpiryDateManager.is_expired")

    def clear(self):
        """
        Clears the expiry date.

        Does not save the object to the database.

        :return: nothing
        """
        raise NotImplementedError("TO-DO: ExpiryDateManager.clear")

    def clear_all(self):
        """
        Clears all object instances where this field is expired given that
        database data provider is the only data provider here.

        Produces one single SQL query to delete all expired objects from the database

        :return: nothing
        """
        raise NotImplementedError("TO-DO: EntityDateManager.clear_all")
