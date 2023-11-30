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
        return not self.force_disable and not settings.CORE_MANAGE_UNIX_GROUPS

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
