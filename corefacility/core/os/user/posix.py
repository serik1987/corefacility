import re
import csv

from .abstract import AbstractUser
from .exceptions import OperatingSystemUserNotFoundException
from .. import CommandMaker, _check_os_posix
from ..group import PosixGroup


class PosixUser(AbstractUser):
    """
    Implements the user interaction mechanism for any kind of POSIX-compatible operating system
    """

    USER_LIST_FILE = "/etc/passwd"
    """ Any POSIX-compliant operating system contains csv-like file where all passwords were stored """

    LOGIN_POSITION = 0
    PASSWORD_PLACEHOLDER_POSITION = 1
    UID_POSITION = 2
    GID_POSITION = 3
    GECOS_POSITION = 4
    HOME_DIRECTORY_POSITION = 5
    SHELL_POSITION = 6

    MINIMUM_UID = 1000
    GECOS_FORMAT = re.compile(r'^(\w*)\s+(\w*),(.*),(.*),(.*)$')
    GECOS_NAME_POSITION = 1
    GECOS_SURNAME_POSITION = 2
    GECOS_PHONE_POSITION = 5

    _password_information = None
    _uid = None
    _gid = None
    _login_shell = None
    _initial_login = None

    @staticmethod
    def extract_gecos_information(gecos_information):
        """
        Extracts name, surname, e-mail and phone from the GECOS information
        :param gecos_information: source GECOS information
        :return: a tuple with the following items: first name, last name, e-mail, phone. If some item is unable to
            extract, None will be placed
        """
        try:
            extracted_information = PosixUser.GECOS_FORMAT.match(gecos_information)
            return (extracted_information[PosixUser.GECOS_NAME_POSITION],
                    extracted_information[PosixUser.GECOS_SURNAME_POSITION],
                    None,
                    extracted_information[PosixUser.GECOS_PHONE_POSITION])
        except Exception:
            return None, None, None, None

    @classmethod
    def get_max_login_chars(cls):
        """
        :return: Maximum characters in the login
        """
        return 32  # Max. login characters in the most of all operating systems

    @classmethod
    def iterate(cls):
        """
        Iterates over all users excluding system users
        :return: generates to be used in the for loop
        """
        with open(cls.USER_LIST_FILE, "r") as user_list_file:
            user_list_reader = csv.reader(user_list_file, delimiter=":")
            for user_info in user_list_reader:
                uid = int(user_info[cls.UID_POSITION])
                if uid >= cls.MINIMUM_UID:
                    name, surname, email, phone = cls.extract_gecos_information(user_info[cls.GECOS_POSITION])
                    user = cls(
                        login=user_info[cls.LOGIN_POSITION],
                        home_directory=user_info[cls.HOME_DIRECTORY_POSITION],
                        login_shell=user_info[cls.SHELL_POSITION],
                        name=name,
                        surname=surname,
                        email=email,
                        phone=phone
                    )
                    user._registered = True
                    user._initial_login = user.login
                    user._password_information = user_info[cls.PASSWORD_PLACEHOLDER_POSITION]
                    user._uid = int(user_info[cls.UID_POSITION])
                    user._gid = int(user_info[cls.GID_POSITION])
                    yield user

    @classmethod
    def find_by_uid(cls, uid):
        """
        Finds the POSIX user by UID. Throws OperatingSystemUserNotFoundException when the user with such UID
        doesn't exist
        :param uid: UID to look for
        :return: a user with a given UID
        """
        for user in cls.iterate():
            if user.uid == uid:
                return user
        raise OperatingSystemUserNotFoundException(uid)

    def __init__(self, login=None, name=None, surname=None, email=None, phone=None, home_directory=None,
                 login_shell="/bin/bash"):
        """
        Creates a copy of the user but doesn't add the user record to the operating system (use create() method
        for such purpose)
        :param login: desired user login
        :param name: the first name
        :param surname: the last name
        :param email: email
        :param phone: phone
        :param home_directory: home directory
        :param login_shell: The shell to be run when the user try to log in using SSH
        """
        _check_os_posix()
        super().__init__(login=login, name=name, surname=surname, email=email, phone=phone,
                         home_directory=home_directory)
        self.login_shell = login_shell

    def __str__(self):
        """
        :return: String representation of the POSIX user object
        """
        return "core.os.user.PosixUser(login={login}, name={name}, surname={surname}, email={email}, phone={phone}, " \
               "UID={uid}, GID={gid}, home_directory={home_directory}, login_shell={login_shell}, " \
               "password_information={password_information}, registered={registered})" \
            .format(
                login=self.login,
                name=self.name,
                surname=self.surname,
                email=self.email,
                phone=self.phone,
                uid=self.uid,
                gid=self.gid,
                home_directory=self.home_dir,
                login_shell=self.login_shell,
                password_information=self.password_information,
                registered=self.registered
            )

    @property
    def password_information(self):
        """
        Any information about the password
        """
        return self._password_information

    @property
    def uid(self):
        """
        UNIX identifier for the user or None if such identifier doesn't exist
        """
        return self._uid

    @property
    def gid(self):
        """
        UNIX GID identifier for the user's primary group
        """
        return self._gid

    @property
    def login_shell(self):
        """
        The default shell to be used when the user will be logged in using SSH
        """
        return self._login_shell

    @login_shell.setter
    def login_shell(self, value):
        if isinstance(value, str):
            self._login_shell = value
        else:
            raise ValueError("Error in POSIX login shell")

    def create(self):
        """
        Creates a user record in the operating system using the information passed as constructor arguments

        :return: nothing
        """
        CommandMaker().add_command(("useradd",
                                    "-c", self._get_gecos_information(),  # Specify the GECOS information
                                    "-d", self.home_dir,  # Specify home directory
                                    "-U",  # Always create group with the same name as user
                                    "-s", self.login_shell,  # Specify default login shell
                                    self.login))
        self._registered = True
        self._initial_login = self.login

    def update(self):
        if not self.registered or self._initial_login is None:
            raise RuntimeError("Please, find the user in the database to modify it")
        CommandMaker().add_command(("usermod",
                                    "-c", self._get_gecos_information(),
                                    "-m", "-d", self.home_dir,
                                    "-l", self.login,
                                    "-s", self.login_shell,
                                    self._initial_login
                                    ))
        self._initial_login = self.login

    def delete(self):
        """
        Deletes a user record from the operating system

        :return: nothing
        """
        if not self.registered or self._initial_login is None:
            raise RuntimeError("Please, find the user in the database to delete it")
        CommandMaker().add_command(("userdel", "-rf", self._initial_login))
        primary_group = PosixGroup.find_by_gid(self.gid)
        CommandMaker().add_command(("sh", "-c", "groupdel %s || echo" % primary_group.name))
        self._initial_login = None
        self._registered = False

    def set_password(self, password):
        """
        Sets the user password
        :param password: a non-encrypted password to be set
        :return: nothing
        """
        if not self.registered:
            raise RuntimeError("Please, add the user to be able to set password")
        CommandMaker().add_command(("passwd", self.login),
                                   input="{0}\n{0}\n".format(password).encode("utf-8"))

    def clear_password(self):
        """
        Clears the user password

        :return: nothing
        """
        if not self.registered:
            raise RuntimeError("Please, add the user to be able to clear password")
        CommandMaker().add_command(("passwd", "-d", self.login))

    def lock(self):
        """
        Locks the user

        :return: nothing
        """
        if not self.registered:
            raise RuntimeError("Please, add user to be able to lock it")
        CommandMaker().add_command(("passwd", "-l", self.login))

    def unlock(self):
        """
        Unlocks the user

        :return: nothing
        """
        if not self.registered:
            raise RuntimeError("Please, add user to be able to unlock it")
        CommandMaker().add_command(("passwd", "-u", self.login))

    def set_groups(self, group_list, is_add=False):
        """
        Sets the group where the user is mentioned
        :param group_list: any iterable of the core.os.group.Group objects or group names
        :param is_add: True if the group list must be added to an existent group list, False if it must be replaced
        :return: nothing
        """
        option = "-aG" if is_add else "-G"
        group_names = []
        for group in group_list:
            if hasattr(group, "name"):
                group_names.append(group.name)
            else:
                group_names.append(group)
        groups = ",".join(group_names)
        CommandMaker().add_command(("usermod", option, groups, self.login))

    def _get_gecos_information(self):
        return "{name} {surname},,,{phone}".format(
            name=self.name,
            surname=self.surname,
            phone=self.phone
        )
