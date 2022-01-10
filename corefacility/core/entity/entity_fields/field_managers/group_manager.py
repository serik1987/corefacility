from core.models import GroupUser
from core.entity.entity_fields.field_managers.entity_value_manager import EntityValueManager
from core.entity.entity_exceptions import EntityOperationNotPermitted
from core.entity.entity_sets.group_set import GroupSet


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
        self._check_system_permissions(group)
        if group not in self:
            group_user = GroupUser(is_governor=False, group_id=group.id, user_id=self.entity.id)
            group_user.save()

    def remove(self, group):
        """
        Removes the user to the group given that the main data source
        for the group is database

        :param group: the group to which the user shall be attached
        :return: nothing
        """
        self._check_system_permissions(group)
        try:
            group_user = GroupUser.objects.get(group_id=group.id, user_id=self.entity.id)
            if group_user.is_governor:
                raise EntityOperationNotPermitted()
            group_user.delete()
        except GroupUser.DoesNotExist:
            pass

    def __contains__(self, group):
        """
        Checks whether the user is within the certain group

        :param group: the group to check
        :return: True is user exists in the group, False otherwise
        """
        self._check_system_permissions(group)
        try:
            group_user = GroupUser.objects.get(group_id=group.id, user_id=self.entity.id)
            return True
        except:
            return False

    def __iter__(self):
        """
        Iterates over all groups to which the user belongs

        :return: the group iterator
        """
        self._check_system_permissions()
        group_set = GroupSet()
        group_set.user = self.entity
        for group in group_set:
            yield group

    def __getitem__(self, index):
        """
        Returns a given item of the list of groups to which the user belongs

        :param index: group index or index range
        :return: a particular group or list of groups
        """
        self._check_system_permissions()
        group_set = GroupSet()
        group_set.user = self.entity
        return group_set[index]

    def _check_system_permissions(self, group=None):
        """
        Checks whether the group user's group list can be manipulated.

        :param group: the group to manipulate with
        :return: nothing
        """
        if self.entity.state in ["creating", "deleted"]:
            raise EntityOperationNotPermitted()
        if group is not None and group.state in ["creating", "deleted"]:
            raise EntityOperationNotPermitted()
