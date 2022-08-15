from django.conf import settings

from core.os.group import PosixGroup

from .posix_provider import PosixProvider
from ...entity import Entity


class ProjectProvider(PosixProvider):
    """
    Allows to create, modify or delete POSIX groups depending on what projects are created, modified or deleted.
    """

    def load_entity(self, project):
        """
        Loads the group from the operating system record
        :param project: a project which corresponding group has to be loaded
        :return: a PosixGroup connecting to the project
        """
        if self.is_provider_on():
            raise NotImplementedError("load_entity")

    def create_entity(self, project):
        """
        Creates the POSIX group based on a given project. Also updates the 'unix_group' field
        :param project: a project which corresponding POSIX group must be created
        :return: nothing
        """
        if self.is_provider_on():
            raise NotImplementedError("create_entity")

    def resolve_conflict(self, project, posix_group):
        """
        Checks the existent POSIX group on whether it corresponds to the project
        :param project: a project that shall be checked
        :param posix_group: a POSIX group to be checked
        :return: nothing
        """
        if self.is_provider_on():
            raise NotImplementedError("resolve_conflict")

    def update_entity(self, project):
        """
        Updates the POSIX group corresponding to the project
        :param project: the project which POSIX group have to be updated
        :return: nothing
        """
        if self.is_provider_on():
            raise NotImplementedError("update_entity")

    def delete_entity(self, project):
        """
        Deletes the POSIX group corresponding to the project
        :param project: the project to be deleted
        :return: nothing
        """
        if self.is_provider_on():
            raise NotImplementedError("delete_entity")

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
        raise NotImplementedError("unwrap_entity")

    def is_provider_on(self):
        """"
        Checks whether POSIX provider is applicable
        :return: True if the provider routines will be applied, False otherwise
        """
        return not self.force_disable and settings.CORE_MANAGE_UNIX_GROUPS
