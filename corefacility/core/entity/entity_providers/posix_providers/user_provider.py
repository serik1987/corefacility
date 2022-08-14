import os
import hashlib
from django.conf import settings

from core.os.user import PosixUser, LockStatus
from core.os.group import PosixGroup
from core.os.user.exceptions import OperatingSystemUserNotFoundException

from .posix_provider import PosixProvider


class UserProvider(PosixProvider):
    """
    The class implements interaction between the POSIX operating system and the user
    """

    @classmethod
    def _get_posix_login(cls, user_login):
        """
        Transforms the user login to 32-symbol POSIX login

        :param user_login: the user's login
        :return: POSIX-compatible login
        """
        if len(user_login) > PosixUser.get_max_login_chars():
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
        if self.is_provider_on():
            login = self._get_posix_login(user.login)
            try:
                posix_user = PosixUser.find_by_login(login)
                return posix_user
            except OperatingSystemUserNotFoundException:
                return None

    def create_entity(self, user):
        """
        Creates a user given that it doesn't exist in the database
        :param user: a user to be created
        :return: nothing
        """
        if self.is_provider_on():
            self._create_posix_user(user)

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
        if self.is_provider_on():
            self._update_gecos_information(given_user, posix_user)
            given_user._home_dir = posix_user.home_dir
            given_user.notify_field_changed("home_dir")
            given_user._unix_group = posix_user.login
            given_user.notify_field_changed("unix_group")

    def update_entity(self, user):
        """
        Sets information to the user

        :param user: the user to which the information shall be set
        :return: nothing
        """
        if self.is_provider_on():
            try:
                if user.unix_group == "" or user.unix_group is None:
                    login = self._get_posix_login(user.login)
                else:
                    login = user.unix_group
                posix_user = PosixUser.find_by_login(login)
                self._update_gecos_information(user, posix_user)
                self._update_lock_status(user, posix_user)
            except OperatingSystemUserNotFoundException:
                self._create_posix_user(user)

    def delete_entity(self, user):
        """
        Deletes the entity from the external entity source

        :param user: the entity to be deleted
        :return: nothing
        """
        if self.is_provider_on():
            login = self._get_posix_login(user.login)
            try:
                posix_user = PosixUser.find_by_login(login)
                posix_user.delete()
            except OperatingSystemUserNotFoundException:
                pass

    def wrap_entity(self, external_object):
        """
        Creates user from the external object
        (to be called by the load_entity routine)
        :param external_object:
        :return:
        """
        if self.is_provider_on():
            raise NotImplementedError("wrap_entity")

    def unwrap_entity(self, user):
        """
        Transforms the User to the PosixUser
        (to be called by the create_entity, update_entity and delete_entity routine)
        :param user: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        if self.is_provider_on():
            raise NotImplementedError("unwrap_entity")

    def is_provider_on(self):
        """
        Defines whether the provider is enabled. When the provider is disabled it applies as if it doesn't present
        in the system

        :return: True if the provider is enabled, False otherwise.
        """
        return not self.force_disable and settings.CORE_MANAGE_UNIX_USERS

    def _create_posix_user(self, user):
        login = self._get_posix_login(user.login)
        home_directory = self._get_home_directory(login)
        posix_user = PosixUser(login=login, name=user.name, surname=user.surname,
            email=user.email, phone=user.phone, home_directory=home_directory)
        posix_user.create()
        user._home_dir = home_directory
        user.notify_field_changed("home_dir")
        user._unix_group = login
        user.notify_field_changed("unix_group")

    def _update_gecos_information(self, given_user, posix_user):
        account_details_changed = False
        for attr in ("name", "surname", "phone"):
            desired_value = getattr(given_user, attr) or ""
            actual_value = getattr(posix_user, attr) or ""
            if actual_value != desired_value:
                setattr(posix_user, attr, desired_value)
                account_details_changed = True
        if account_details_changed:
            posix_user.update()

    def _update_lock_status(self, given_user, posix_user):
        is_password = len(repr(given_user.password_hash)) > 0
        if is_password and given_user.is_locked and posix_user.is_locked() != LockStatus.LOCKED:
            posix_user.lock()
        if is_password and not given_user.is_locked and posix_user.is_locked() != LockStatus.PASSWORD_SET:
            posix_user.unlock()