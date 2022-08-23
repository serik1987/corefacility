from django.conf import settings
from django.db import transaction

from core.entity.entity_fields.field_managers.entity_value_manager import EntityValueManager
from core.entity.entity_exceptions import EntityOperationNotPermitted
from core.entity.entity_sets.user_set import UserSet
from core.models import GroupUser
from core.transaction import CorefacilityTransaction


class UserManager(EntityValueManager):
    """
    Manages all users containing in a certain group

    The class provides writing facilities to this property.
    Use UserSet for reading facilities
    """

    _permission_provider = None

    @property
    def permission_provider(self):
        if self._permission_provider is None:
            from core.entity.entity_providers.posix_providers.permission_provider import PermissionProvider
            self._permission_provider = PermissionProvider()
        return self._permission_provider

    def add(self, user):
        """
        Adds the user to the group given that the main group source is database

        :param user: the user to be added to the group
        :return: nothing
        """
        self._check_system_permissions(user)
        if not self.exists(user):
            with self._get_transaction_mechanism():
                group_user = GroupUser(is_governor=False, group_id=self.entity.id, user_id=user.id)
                group_user.save()
                self.permission_provider.update_group_list(user)

    def remove(self, user):
        """
        Removes certain user from the group given that the main group source is database

        :param user: the user to remove
        :return: nothing
        """
        self._check_system_permissions(user)
        if user.id == self.entity.governor.id:
            raise EntityOperationNotPermitted()
        with self._get_transaction_mechanism():
            try:
                GroupUser.objects.get(group_id=self.entity.id, user_id=user.id).delete()
                self.permission_provider.update_group_list(user)
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

    def _get_transaction_mechanism(self):
        return CorefacilityTransaction() if not self.permission_provider.force_disable else transaction.atomic()
