from .entity_value_manager import EntityValueManager


class GroupManager(EntityValueManager):
    """
    Allows any user to manage all its groups

    The manages provides writing facilities only. UserSet is responsible for reading facilities
    """

    def add(self, group):
        """
        Attaches the user to the group given that the main data source
        for the group is database

        :param group: the group to which the user shall be attached
        :return: nothing
        """
        raise NotImplementedError("TO-DO: GroupManager.add")

    def remove(self, group):
        """
        Removes the user to the group given that the main data source
        for the group is database

        :param group: the group to which the user shall be attached
        :return: nothing
        """
        raise NotImplementedError("TO-DO: GroupManager.remove")

    def __iter__(self):
        """
        Iterates over all groups to which the user belongs

        :return: the group iterator
        """
        raise NotImplementedError("TO-DO: GroupManager.__iter__")

    def __getitem__(self, index):
        """
        Returns a given item of the list of groups to which the user belongs

        :param index: group index or index range
        :return: a particular group or list of groups
        """
        raise NotImplementedError("TO-DO: GroupManager.__getitem__")
