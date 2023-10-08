import os
import stat

from django.conf import settings

from ....entity.entity_sets.user_set import UserSet

from .files_provider import FilesProvider


class ProjectFilesProvider(FilesProvider):
    """
    Creates, modifies or deletes the project directory in response to creating, modifying or deleting the project
    itself
    """

    DESIRED_PERMISSIONS = 0o2750

    @staticmethod
    def project_directory_name_from_alias(alias):
        """
        Returns the full project directory name for a given project alias
        :param alias: the project alias
        :return: nothing
        """
        return os.path.join(settings.CORE_PROJECT_BASEDIR, "proj." + alias)

    @property
    def is_provider_on(self):
        """
        True if provider is switched on, False otherwise
        """
        return not self.force_disable

    @property
    def is_permission_on(self):
        """
        True if permissions set are switched on, False otherwise
        """
        return not self.force_disable and settings.CORE_MANAGE_UNIX_GROUPS

    def change_dir_permissions(self, maker, project, dir_name):
        posix_user_name = project.governor.unix_group
        if posix_user_name is None:
            posix_user_name = UserSet().get(project.governor.id).unix_group
        raise NotImplementedError("TO-DO: find POSIX user")
        raise NotImplementedError("TO-DO: find POSIX group")
        try:
            posix_user = PosixUser.find_by_login(posix_user_name)
            owner_user = posix_user.login
            owner_uid = posix_user.uid
        except OperatingSystemUserNotFoundException:
            owner_user = "root"
            owner_uid = 0
        try:
            posix_group = PosixGroup.find_by_name(project.unix_group)
            owner_group = posix_group.name
            owner_gid = posix_group.gid
        except OperatingSystemGroupNotFound:  # the group will be created after CorefacilityTransaction completion
            owner_group = project.unix_group
            owner_gid = -1  # GID for some non-existent group
        try:
            directory_info = os.stat(dir_name)
            owner_change = directory_info.st_uid != owner_uid
            group_change = directory_info.st_gid != owner_gid
            permission_change = stat.S_IMODE(directory_info.st_mode) != self.DESIRED_PERMISSIONS
        except FileNotFoundError:
            owner_change = True
            group_change = True
            owner_group = project.unix_group
            permission_change = True
        maker = CommandMaker()
        if owner_change or group_change:
            maker.add_command(("chown", "%s:%s" % (owner_user, owner_group), dir_name))
        if permission_change:
            maker.add_command(("chmod", "0%o" % self.DESIRED_PERMISSIONS, dir_name))

    def update_entity(self, project):
        """
        Updates the project's directory in response to the directory update
        :param project: the project which directory shall be updated
        :return: nothing
        """
        if self.is_provider_on:
            old_project_dir = project.project_dir
            new_project_dir = self.project_directory_name_from_alias(project.alias)
            if old_project_dir != new_project_dir and os.path.isdir(old_project_dir):
                if self.is_permission_on:
                    raise NotImplementedError("TO-DO: rename the project directory for the Linux server")
                else:
                    os.rename(old_project_dir, new_project_dir)
            self.update_dir_info(project, new_project_dir)

    def unwrap_entity(self, project):
        """
        Returns the full path to the project directory
        :param project: the project which home directory must be revealed
        :return: nothing
        """
        if project.project_dir is not None:
            return project.project_dir
        else:
            return self.project_directory_name_from_alias(project.alias)

    def update_dir_info(self, project, dir_name):
        """
        Inserts the project's directory name to the corresponding project field
        :param project: the project which fields shall be updated
        :param dir_name: full name of its directory
        :return: nothing
        """
        project._project_dir = dir_name
        project.notify_field_changed("project_dir")
