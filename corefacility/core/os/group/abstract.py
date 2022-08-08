from .exceptions import OperatingSystemGroupNotFound


class AbstractGroup:
    """
    Base class for any group information.
    """

    MAX_GROUP_NAME_LENGTH = -1
    """ Defines maximum number of characters in the group name """

    _name = None
    _registered = None

    @classmethod
    def iterate(cls):
        """
        Iterates over all groups

        :return: Generator that shall be used in for loop to iterate over all POSIX groups
        """
        raise NotImplementedError("iterate [class method]")

    @classmethod
    def find_by_name(cls, name):
        """
        Finds the group with a given name
        :param name: a search string
        :return: the AbstractGroup instance corresponding to a group with a given name
        """
        for group in cls.iterate():
            if group.name == name:
                return group
        raise OperatingSystemGroupNotFound(name)

    def __init__(self, name):
        """
        Initializes the group but doesn't add it to the operating system
        :param name: the group name
        """
        self.name = name
        self._registered = False

    @property
    def name(self):
        """
        Returns the group name
        """
        return self._name if self._name is not None else ""

    @name.setter
    def name(self, value):
        """
        Sets the group name
        :param value: the group name
        :return: nothing
        """
        if isinstance(value, str) and 0 < len(value) <= self.MAX_GROUP_NAME_LENGTH:
            self._name = value
        else:
            raise ValueError("'%s' is incorrect value for the group name" % value)

    @property
    def registered(self):
        """
        True if the group record has been added to the operating system, False otherwise
        """
        return self._registered

    def create(self):
        """
        Adds the group record to the operating system

        :return: nothing
        """
        raise NotImplementedError("create")

    def update(self):
        """
        Changes information about the group in the operating system

        :return: nothing
        """
        raise NotImplementedError("update")

    def delete(self):
        """
        Deletes the group

        :return: nothing
        """
        raise NotImplementedError("delete")
