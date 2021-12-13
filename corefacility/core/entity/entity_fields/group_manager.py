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
