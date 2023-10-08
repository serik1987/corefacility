from .entity_set_object import EntitySetObject


class ExternalAccountSetObject(EntitySetObject):
    """
    This is the base class for test set of any external account
    """

    MIN_USER_LENGTH = 10

    _user_set_object = None

    def __init__(self, user_set_object, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param user_set_object: The user set object participating in the account
        :param _entity_list: This is an internal argument. Don't use it.
        """
        self._user_set_object = user_set_object
        if len(self._user_set_object) < self.MIN_USER_LENGTH:
            raise ValueError("ExternalAccountSetObject: the user set object must contain at least 10 users")
        super().__init__(_entity_list)

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self._user_set_object, _entity_list=list(self._entities))

    def filter_by_user(self, user):
        """
        Filters the dataset by user

        :param user: the user according to which all accounts must be filtered
        :return: nothing
        """
        self._entities = list(filter(lambda account: account.user.id == user.id, self._entities))
