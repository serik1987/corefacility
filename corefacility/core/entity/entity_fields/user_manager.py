from .entity_value_manager import EntityValueManager
from ..entity_exceptions import EntityOperationNotPermitted
from ..entity_sets.user_set import UserSet
from ...models import GroupUser


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
        self._check_system_permissions(user)
        if not self.exists(user):
            group_user = GroupUser(is_governor=False, group_id=self.entity.id, user_id=user.id)
            group_user.save()

    def remove(self, user):
        """
        Removes certain user from the group given that the main group source is database

        :param user: the user to remove
        :return: nothing
        """
        self._check_system_permissions(user)
        if user.id == self.entity.governor.id:
            raise EntityOperationNotPermitted()
        try:
            GroupUser.objects.get(group_id=self.entity.id, user_id=user.id).delete()
        except GroupUser.DoesNotExist:
            pass

    def exists(self, user):
        """
        Checks for user existence

        :param user: user which existence must be checked
        :return: nothing
        """
        self._check_system_permissions(user)
        try:
            GroupUser.objects.get(group_id=self.entity.id, user_id=user.id)
            return True
        except GroupUser.DoesNotExist:
            return False

    def __iter__(self):
        """
        iterates over all users in the group

        :return: All users in the group
        """
        self._check_system_permissions()
        user_set = UserSet()
        user_set.group = self.entity
        for user in user_set:
            yield user

    def __getitem__(self, index):
        """
        Returns a user with a given index

        :param index: the user index or range of indices
        :return: list of users
        """
        self._check_system_permissions()
        user_set = UserSet()
        user_set.group = self.entity
        return user_set[index]

    def __len__(self):
        """
        Returns total number of users in the group

        :return: total number of users in the group
        """
        self._check_system_permissions()
        user_set = UserSet()
        user_set.group = self.entity
        return len(user_set)

    def _check_system_permissions(self, user=None):
        """
        Checks whether the group state allows any modification a user list

        :param user: the user that is going to be added or removed in the group of None if user list is going to be
            accessed
        :return: nothing
        """
        if self.entity.state in ['creating', 'deleted']:
            raise EntityOperationNotPermitted()
        if user is not None and user.state in ['creating', 'deleted']:
            raise EntityOperationNotPermitted()
