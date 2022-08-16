import zlib
from django.conf import settings

from core.os.group import PosixGroup, OperatingSystemGroupNotFound

from .posix_provider import PosixProvider
from ...entity import Entity


class ProjectProvider(PosixProvider):
    """
    Allows to create, modify or delete POSIX groups depending on what projects are created, modified or deleted.
    """

    MAX_GROUP_NAME_LENGTH = 10

    @staticmethod
    def _get_posix_group_name(alias):
        if len(alias) > ProjectProvider.MAX_GROUP_NAME_LENGTH:
            return "p" + str(zlib.crc32(alias.encode("utf-8")))[:11]
        else:
            return alias

    def load_entity(self, project):
        """
        Loads the group from the operating system record
        :param project: a project which corresponding group has to be loaded
        :return: a PosixGroup connecting to the project
        """
        if self.is_provider_on():
            group_name = self._get_posix_group_name(project.alias)
            try:
                return PosixGroup.find_by_name(group_name)
            except OperatingSystemGroupNotFound:
                return None

    def create_entity(self, project):
        """
        Creates the POSIX group based on a given project. Also updates the 'unix_group' field
        :param project: a project which corresponding POSIX group must be created
        :return: nothing
        """
        if self.is_provider_on():
            self._create_posix_group(project)

    def resolve_conflict(self, project, posix_group):
        """
        Checks the existent POSIX group on whether it corresponds to the project
        :param project: a project that shall be checked
        :param posix_group: a POSIX group to be checked
        :return: nothing
        """
        if self.is_provider_on():
            project._unix_group = posix_group.name
            project.notify_field_changed("unix_group")

    def update_entity(self, project):
        """
        Updates the POSIX group corresponding to the project
        :param project: the project which POSIX group have to be updated
        :return: nothing
        """
        if self.is_provider_on():
            try:
                posix_group = self.unwrap_entity(project)
                self._update_posix_group(project, posix_group)
            except OperatingSystemGroupNotFound:
                self._create_posix_group(project)

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
        if project.unix_group == "" or project.unix_group is None:
            group_alias = self._get_posix_group_name(project.alias)
        else:
            group_alias = project.unix_group
        return PosixGroup.find_by_name(group_alias)

    def is_provider_on(self):
        """"
        Checks whether POSIX provider is applicable
        :return: True if the provider routines will be applied, False otherwise
        """
        return not self.force_disable and settings.CORE_MANAGE_UNIX_GROUPS

    def _create_posix_group(self, project):
        """
        Creates the UNIX group based on a given project
        :param project: a project which group must be created
        :return: corresponding UNIX group
        """
        group_name = self._get_posix_group_name(project.alias)
        posix_group = PosixGroup(name=group_name)
        posix_group.create()
        project._unix_group = group_name
        project.notify_field_changed("unix_group")
        return posix_group

    def _update_posix_group(self, project, posix_group):
        """
        Changes the UNIX group name if this is necessary
        :param project: a corresponding project entity
        :param posix_group: POSIX group which name must be changed
        :return: nothing
        """
        actual_group_name = posix_group.name
        desired_group_name = self._get_posix_group_name(project.alias)
        if actual_group_name != desired_group_name:
            posix_group.name = desired_group_name
            posix_group.update()
            project._unix_group = desired_group_name
            project.notify_field_changed("unix_group")
