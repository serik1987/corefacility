from django.db import transaction

from .permission_manager import PermissionManager
from ..entity_sets.access_level_set import AccessLevelSet
from ...exceptions.entity_exceptions import EntityOperationNotPermitted
from ..group import Group


class ProjectPermissionManager(PermissionManager):
    """
    Manages access control lists for a particular project.
    """

    _permission_model = "ru.ihna.kozhukhov.core_application.models.permission.Permission"
    """ Defines particular model connects your entity model, the Group model and particular access level """

    _permission_table = "core_application_permission"
    """ Defines the SQL table where permission information is stored """

    _entity_link_field = "project_id"
    """ Defines a link that connects particular entity to the permission model mentioned above """

    _full_access = None
    _permission_provider = None

    @property
    def full_access(self):
        if self._full_access is None:
            from ..entity_sets.access_level_set import AccessLevelSet
            self._full_access = AccessLevelSet.project_level("full")
        return self._full_access

    @property
    def permission_provider(self):
        if self._permission_provider is None:
            from ..providers.posix_providers.permission_provider import PermissionProvider
            self._permission_provider = PermissionProvider()
        return self._permission_provider

    def __iter__(self):
        """
        Iterates over all permission set
        """
        yield self.entity.root_group, self.full_access
        for group, access_level in super().__iter__():
            yield group, access_level

    def set(self, group, access_level):
        """
        Sets the access level to a particular group.

        :param group: a group to which access level must be set or None if access level shall be set for the rest
            of users
        :param access_level: the access level to set (an instance of AccessLevel entity)
        :return: nothing
        """
        if self.is_root_group(group):
            raise EntityOperationNotPermitted()
        else:
            with self._get_transaction_mechanism():
                old_access_level = self.get(group)
                super().set(group, access_level)
                self.permission_provider.update_access_level(self.entity, group, old_access_level, access_level)

    def get(self, group):
        """
        Reads access level for a certain group.

        WARNING. The method is not optimized according to the number of SQL queries. Use the 'user' filter in the
        ProjectSet for full and comprehensive information.

        :param group: a group to which access level must be set or None if access level shall be set for the rest
            of users
        :return: the AccessLevel entity reflecting a certain access level for the group.
        """
        if self.is_root_group(group):
            return self.full_access
        else:
            return super().get(group)

    def delete(self, group):
        """
        Removes the access level for a certain group

        :param group: the group for which the access level shall be removed.
        :return: nothing
        """
        if self.is_root_group(group):
            raise EntityOperationNotPermitted()
        else:
            with self._get_transaction_mechanism():
                old_access_level = self.get(group)
                new_access_level = AccessLevelSet().get('no_access')
                super().delete(group)
                self.permission_provider.update_access_level(self.entity, group, old_access_level, new_access_level)

    def is_root_group(self, group):
        """
        Checks whether certain group is root group

        :param group: the group to test
        :return: True if and only if: a. the group is a Group entity, b. the project root group is defined,
            c. the group has the same ID as the project root group
        """
        return isinstance(group, Group) and \
            self.entity.root_group is not None and \
            group.id == self.entity.root_group.id

    def _get_transaction_mechanism(self):
        """
        @return always transaction.atomic
        """
        return transaction.atomic()
