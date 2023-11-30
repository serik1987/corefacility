import zlib
from django.conf import settings

from ru.ihna.kozhukhov.core_application.management.commands.autoadmin.auto_admin_wrapper_object import \
    AutoAdminWrapperObject
from ru.ihna.kozhukhov.core_application.management.commands.autoadmin.posix_group import PosixGroup
from .posix_provider import PosixProvider


class ProjectProvider(PosixProvider):
    """
    Allows to create, modify or delete POSIX groups depending on what projects are created, modified or deleted.
    """

    MAX_GROUP_NAME_LENGTH = 10

    _permission_provider = None

    @property
    def permission_provider(self):
        if self._permission_provider is None:
            from .permission_provider import PermissionProvider
            self._permission_provider = PermissionProvider()
        return self._permission_provider

    def load_entity(self, project):
        """
        Loads the group from the operating system record
        :param project: a project which corresponding group has to be loaded
        :return: a PosixGroup connecting to the project
        """
        pass

    def create_entity(self, project):
        """
        Creates the POSIX group based on a given project. Also updates the 'unix_group' field
        :param project: a project which corresponding POSIX group must be created
        :return: nothing
        """
        if self.is_provider_on():
            posix_group = self.unwrap_entity(project)
            posix_group.create()

    def resolve_conflict(self, project, posix_group):
        """
        Checks the existent POSIX group on whether it corresponds to the project
        :param project: a project that shall be checked
        :param posix_group: a POSIX group to be checked
        :return: nothing
        """
        pass

    def update_entity(self, project):
        """
        Updates the POSIX group corresponding to the project
        :param project: the project which POSIX group have to be updated
        :return: nothing
        """
        if self.is_provider_on():
            posix_group = self.unwrap_entity(project)
            if 'alias' in project._edited_fields:
                posix_group.update_alias()
            if 'root_group' in project._edited_fields:
                posix_group.update_root_group(project._old_root_group_id)
                project._old_root_group_id = None

    def delete_entity(self, project):
        """
        Deletes the POSIX group corresponding to the project
        :param project: the project to be deleted
        :return: nothing
        """
        if self.is_provider_on():
            posix_group = self.unwrap_entity(project)
            posix_group.delete()

    def wrap_entity(self, external_object):
        """
        Useless function
        :param external_object:
        :return: nothing
        """
        pass

    def unwrap_entity(self, project):
        """
        Looks for the POSIX group corresponding to the project
        :param project: a project which POSIX group shall be found
        :return: a given POSIX group
        """
        return AutoAdminWrapperObject(PosixGroup, project)

    def is_provider_on(self):
        """"
        Checks whether POSIX provider is applicable
        :return: True if the provider routines will be applied, False otherwise
        """
        return not self.force_disable and settings.CORE_MANAGE_UNIX_GROUPS
