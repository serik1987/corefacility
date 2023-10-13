import csv
import os
import re
import uuid

from django.conf import settings

from ....entity.entity_sets.user_set import UserSet
from ....exceptions.entity_exceptions import ConfigurationProfileException
from .auto_admin_object import AutoAdminObject


class PosixUser(AutoAdminObject):
    """
    Reading, changing, updating and deleting POSIX users.
    """

    MAX_LOGIN_SIZE = 32
    """ Maximum size of POSIX login, in characters """

    MAX_LOGIN_TRIALS = 1_000
    """ Maximum number of attempts to select a distinguishable login """

    ENUMERATED_USER_TEMPLATE = re.compile(r"^(.*)(\d+)$")

    POSIX_USER_FILE = "/etc/passwd"
    """ Location of the file with POSIX users """

    login = None
    """ The POSIX login for the user """

    LOGIN_POSITION = 0
    """ Position of the user login within the /etc/passwd """

    home_dir = None
    """ The user's home directory """

    HOME_DIR_POSITION = 5
    """ Position of the home directory within the /etc/passwd """

    entity = None

    @classmethod
    def update_static_objects(cls):
        """
        An auto admin object has some kind of static objects (e.g., POSIX users or group already registered in the
        operating system).

        Use this method to update the object list. Primarily, the method should be run at the beginning of the
        auto admin cycle
        """
        cls._static_objects = []
        with open(cls.POSIX_USER_FILE, 'r') as posix_users_file:
            posix_users_reader = csv.reader(posix_users_file, delimiter=':')
            for posix_user_info in posix_users_reader:
                posix_user = cls(None,
                                 login=posix_user_info[cls.LOGIN_POSITION],
                                 home_dir=posix_user_info[cls.HOME_DIR_POSITION]
                                 )
                cls._static_objects.append(posix_user)

    def __init__(self, entity, login=None, home_dir=None):
        """
        Creates new PosixUser object

        :param entity: corefacility user this given user relates to (either User object or user ID)
        :param login: POSIX user login if not specified
        """
        super().__init__()
        if entity is None and (login is None or home_dir is None):
            raise ValueError("either entity or both login and home_dir arguments shall not be None")
        if not settings.CORE_MANAGE_UNIX_USERS:
            raise ConfigurationProfileException(settings.CONFIGURATION)
        if isinstance(entity, int):
            entity = UserSet().get(entity)
        if entity is not None:
            self.login = entity.unix_group
            self.home_dir = entity.home_dir
            self.entity = entity
            self.log = entity.log
        else:
            self.login = login
            self.home_dir = home_dir
            self.entity = None

    @property
    def entity_id(self):
        """
        ID of the corefacility user that has been attached to a given user. None if no user was attached.
        """
        if self.entity is not None:
            return self.entity.id
        else:
            return None

    def create(self):
        """
        Creating new POSIX user.

        :return: None
        """
        if self.login is None or self.home_dir is None:
            self.login = self._shorten_user_login(self.entity.login)
            self.home_dir = os.path.join(settings.CORE_PROJECT_BASEDIR, "u-" + self.login)
        result = self.run(
            (
                "useradd",
                "-d", self.home_dir,
                "-m",
                "-U",
                "-c", "corefacility user %d" % self.entity_id,
                self.login
            )
        )
        print(result)

    def update(self):
        """
        Change a given POSIX user in such a way as it corresponds to a given corefacility user

        :return: None
        """
        print("UPDATE USER")
        print(self)

    def delete(self):
        """
        Removes the POSIX user from the database

        :return: None
        """
        print("DELETE USER")
        print(self)

    def __str__(self):
        return "PosixUser(login={login}, home_dir={home_dir}, corefacility_user_id={id})".format(
            login=self.login,
            home_dir=self.home_dir,
            id=self.entity_id
        )

    def _shorten_user_login(self, login):
        """
        Generates the POSIX login for the UNIX user base on its corefacility login

        :param login: the corefacility login, up to 100 symbols
        :return: the POSIX user login, up to 32 symbols
        """
        if len(login) > self.MAX_LOGIN_SIZE:
            login = login[:self.MAX_LOGIN_SIZE]
        available_logins = [posix_user.login for posix_user in self.get_static_objects()]
        trials = 0
        while login in available_logins:
            enumerated_login_parts = self.ENUMERATED_USER_TEMPLATE.match(login)
            if enumerated_login_parts is None:  # Non-enumerated login
                login += "1"
            else:
                constant_part, varying_part = enumerated_login_parts.group(1, 2)
                new_varying_part = str(int(varying_part) + 1)
                login = constant_part + new_varying_part
                if len(login) > self.MAX_LOGIN_SIZE:
                    extra_chars = len(login) - self.MAX_LOGIN_SIZE
                    login = login[extra_chars:]
            trials += 1
            if trials > self.MAX_LOGIN_TRIALS:
                login = uuid.uuid4().hex
        return login
