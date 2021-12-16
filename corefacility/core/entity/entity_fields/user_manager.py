from .entity_value_manager import EntityValueManager


class UserManager(EntityValueManager):
    """
    Manages all users containing in a certain group

    The class provides writing facilities to this property.
    Use UserSet for reading facilities
    """

    def add(self, user):
        """
        Adds the user to the group given that the main group source is database

        :param user: the user to be added to the group
        :return: nothing
        """
        raise NotImplementedError("TO-DO: UserManager.add")

    def remove(self, user):
        """
        Removes certain user from the group given that the main group source is database

        :param user: the user to remove
        :return: nothing
        """
        raise NotImplementedError("TO-DO: UserManager.remove")

    def __iter__(self):
        """
        iterates over all users in the group

        :return: All users in the group
        """
        raise NotImplementedError("TO-DO: UserManager.__iter__")

    def __getitem__(self, index):
        """
        Returns a user with a given index

        :param index: the user index or range of indices
        :return: list of users
        """
        raise NotImplementedError("TO-DO: UserManager.__getitem__")
