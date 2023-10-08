import os
import stat

from django.conf import settings

from .files_provider import FilesProvider


class UserFilesProvider(FilesProvider):
    """
    Creates, modifies or destroys the user's home directory in response to create, modify or destroy the user itself
    """

    HOME_DIRECTORY_MODE = 0o4750

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
        return not self.force_disable and settings.CORE_MANAGE_UNIX_USERS

    def change_dir_permissions(self, maker, user, dir_name):
        raise NotImplementedError('change_dir_permissions')

    def update_entity(self, user):
        """
        Changes the user's home directory given that login has been changed
        :param user: the user to be updated
        :return: nothing
        """
        if self.is_provider_on \
                and "login" in user._edited_fields and \
                not settings.CORE_MANAGE_UNIX_USERS and \
                os.path.isdir(user.home_dir):
            new_home_dir = os.path.join(settings.CORE_PROJECT_BASEDIR, user.login)
            os.rename(user.home_dir, new_home_dir)
            user._home_dir = new_home_dir
            user.notify_field_changed("home_dir")

    def unwrap_entity(self, user):
        """
        Returns the user's home directory
        :param user: the user which home directory must be entered
        :return: nothing
        """
        if user.home_dir is not None:
            return user.home_dir
        else:
            return os.path.join(settings.CORE_PROJECT_BASEDIR, user.login)

    def update_dir_info(self, user, dir_name):
        """
        Inserts the directory name to the entity field
        :param user: the entity to which field the directory name should be inserted
        :param dir_name: full directory path
        :return: nothing
        """
        user._home_dir = dir_name
        user.notify_field_changed("home_dir")
