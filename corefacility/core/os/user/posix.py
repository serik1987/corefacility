import re
import csv

from .abstract import AbstractUser
from .exceptions import OperatingSystemUserNotFoundException


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
    GECOS_FORMAT = re.compile(r'^(\w+)\s+(\w+),(.+),(.+),(.+)$')
    GECOS_NAME_POSITION = 1
    GECOS_SURNAME_POSITION = 2
    GECOS_PHONE_POSITION = 5

    _password_information = None
    _uid = None
    _gid = None
    _login_shell = None

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
            return extracted_information[PosixUser.GECOS_NAME_POSITION], \
                extracted_information[PosixUser.GECOS_SURNAME_POSITION], \
                None, \
                extracted_information[PosixUser.GECOS_PHONE_POSITION]
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
        super().__init__(login=login, name=name, surname=surname, email=email, phone=phone,
                         home_directory=home_directory)
        self._login_shell = login_shell

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
