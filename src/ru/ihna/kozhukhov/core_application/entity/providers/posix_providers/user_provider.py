import os
import hashlib
from django.conf import settings

from ....management.commands.autoadmin.posix_user import PosixUser
from ....management.commands.autoadmin.auto_admin_wrapper_object import AutoAdminWrapperObject
from .posix_provider import PosixProvider


class UserProvider(PosixProvider):
    """
    The class implements interaction between the POSIX operating system and the user
    """

    MAX_LOGIN_CHARS = 32

    @classmethod
    def _get_posix_login(cls, user_login):
        """
        Transforms the user login to 32-symbol POSIX login
        :param user_login: the user's login
        :return: POSIX-compatible login
        """
        if len(user_login) > cls.MAX_LOGIN_CHARS:
            return hashlib.md5(user_login.encode("utf-8")).hexdigest()
        else:
            return user_login

    @classmethod
    def _get_home_directory(cls, login):
        return os.path.join(settings.CORE_PROJECT_BASEDIR, login)

    def load_entity(self, user):
        """
        Loads the user from the POSIX record
        :param user: The user that shall be found in the operating system
        :return: the PosixUser instance if the user exists or None otherwise
        """
        pass

    def create_entity(self, user):
        """
        Creates a user given that it doesn't exist in the database
        :param user: a user to be created
        :return: nothing
        """
        if self.is_provider_on():
            self.unwrap_entity(user).create()

    def resolve_conflict(self, given_user, posix_user):
        """
        This function is called when the user tries to save the entity when another duplicated entity
        exists in this entity source.

        The aim of this function is to resolve the underlying conflict and probably call the
        'create_entity' function again.

        :param given_user: the entity the user tries to save
        :param posix_user: the entity duplicate that has already been present on given entity source
        :return: nothing but must throw an exception when such entity can't be created
        """
        pass

    def update_entity(self, user):
        """
        Sets information to the user
        :param user: the user to which the information shall be set
        :return: nothing
        """
        if self.is_provider_on():
            self.unwrap_entity(user).update()

    def delete_entity(self, user):
        """
        Deletes the entity from the external entity source
        :param user: the entity to be deleted
        :return: nothing
        """
        if self.is_provider_on():
            self.unwrap_entity(user).delete()

    def wrap_entity(self, external_object):
        """
        Creates user from the external object
        (to be called by the load_entity routine)
        :param external_object:
        :return:
        """
        pass

    def unwrap_entity(self, user):
        """
        Transforms the User to the PosixUser
        (to be called by the create_entity, update_entity and delete_entity routine)
        :param user: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        return AutoAdminWrapperObject(PosixUser, user)

    def is_provider_on(self):
        """
        Defines whether the provider is enabled. When the provider is disabled it applies as if it doesn't present
        in the system

        :return: True if the provider is enabled, False otherwise.
        """
        return not self.force_disable and settings.CORE_MANAGE_UNIX_USERS
