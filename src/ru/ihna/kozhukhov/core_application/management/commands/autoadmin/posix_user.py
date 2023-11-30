import csv
import os
import re
import subprocess
import uuid

from django.conf import settings

from ....entity.entity_sets.user_set import UserSet
from ....entity.providers.model_providers.user_provider import UserProvider
from ....exceptions.entity_exceptions import ConfigurationProfileException, RetryCommandAfterException
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
    """ Template for enumerated users, i.e., user1, user2, ... """

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

    gid = None
    """ User's primary GID or None if we don't know about this """

    GID_POSITION = 3
    """ Position of the user's primary GID """

    entity = None

    @classmethod
    def get_posix_users(cls):
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
                posix_user.gid = posix_user_info[cls.GID_POSITION]
                cls._static_objects.append(posix_user)
        return cls._static_objects

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
        output = self.run(
            (
                # see 'man useradd' shell command for more details
                "useradd",
                "-d", self.home_dir,                                # Specifies the user's home directory
                "-m",                                               # Tells UNIX to create the users' home directory
                "-U",                                               # Tells UNIX to create user's primary group
                "-c", "corefacility user %d" % self.entity_id,      # Comment string to add to /etc/passwd
                self.login                                          # The POSIX login of the user
            )
        )
        self._update_database_info()
        return output

    def check_user_for_update(self):
        """
        Finds user with the same name as a given user
        :return: the user with the same name (but not the same PosixUser entity!) at success, None at failure
        """
        if self.login is None or self.home_dir is None:
            raise RetryCommandAfterException()
        available_posix_user = None
        available_posix_users = filter(lambda user: user.login == self.login, self.get_posix_users())
        for user in available_posix_users:
            available_posix_user = user
            break
        return available_posix_user

    def update_login(self):
        """
        Change a given POSIX user in such a way as it corresponds to a given corefacility user

        :return: None
        """
        output = ""
        available_posix_user = self.check_user_for_update()
        if available_posix_user:
            old_login = self.login
            self.login = self._shorten_user_login(self.entity.login)
            self.home_dir = os.path.join(settings.CORE_PROJECT_BASEDIR, "u-" + self.login)
            output = self.run(
                (
                    "usermod",
                    "-m", "-d", self.home_dir,                  # Change the home directory
                    "-l", self.login,                           # Also change the user's login
                    old_login                                   # Old user's login
                )
            )
            self._update_database_info()
        else:
            self.login = None
            self.home_dir = None
            output = self.create()
        return output

    def set_password(self, new_password):
        """
        Sets the new user's password
        :param new_password: new password to set
        :return: string containing the output information
        """
        output = ""
        available_posix_user = self.check_user_for_update()
        if not available_posix_user:
            self.create()
        output = self.run(
            ("passwd", self.login, ),
            # The input is required to answer the following question:
            # Type new password: ******
            # Re-type new password: ******
            #
            # Putting the password into the command is very bad idea because all commands are (a) logged;
            # (b) sent using E-mail
            input="{0}\n{0}".format(new_password).encode("utf-8"),
        )
        self.update_lock()
        return output

    def update_lock(self):
        """
        Updates the user's lock
        :return: string containing output information
        """
        output = ""
        available_posix_user = self.check_user_for_update()
        if not available_posix_user:
            self.create()
        desired_lock_status = self.entity.is_locked
        actual_lock_status = subprocess.run(
            ("passwd", "-S", self.login),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        actual_lock_status = actual_lock_status \
            .stdout \
            .decode('utf-8') \
            .split()[1]
        if actual_lock_status.upper() == 'NP':  # When the password is not set, the POSIX accounts can't
                                        # be distinguished by
                                        # 'locked' and 'non-locked', i.e.: all accounts are locked on the level of the
                                        # operating system
            return
        elif actual_lock_status.upper() == 'P':  # Password was set, the account is unlocked
            actual_lock_status = False
        elif actual_lock_status.upper() == 'L':  # Password was set but the account is locked
            actual_lock_status = True
        else:
            raise ValueError("Undocumented lock status '%s' for POSIX account '%s'" % (actual_lock_status, self.login))
        if desired_lock_status and not actual_lock_status:
            output = self.run(('passwd', '-l', self.login))
        if not desired_lock_status and actual_lock_status:
            output = self.run(('passwd', '-u', self.login))
        return output

    def update_supplementary_groups(self, exclude=None):
        """
        Updates all supplementary groups for the user, according to what project it belongs to.

        :param exclude: name of the POSIX group to exclude from the group list or None, if don't do this.
        """
        output = ""
        available_posix_user = self.check_user_for_update()
        if not available_posix_user:
            self.create()

        from ru.ihna.kozhukhov.core_application.entity.project import ProjectSet
        posix_group_list = set()
        project_set = ProjectSet()
        project_set.user = self.entity
        project_dictionary = dict()
        for project in project_set:
            if project.unix_group:
                posix_group_list.add(project.unix_group)
                project_dictionary[project.unix_group] = project
        if exclude is not None:
            posix_group_list.remove(exclude)
            del project_dictionary[exclude]

        if self.home_dir:
            for filename in os.listdir(self.home_dir):
                filename = os.path.join(self.home_dir, filename)
                if not os.path.islink(filename):
                    continue
                target = os.readlink(filename)
                related_unix_group = None
                for unix_group, project in project_dictionary.items():
                    if project.project_dir == target:
                        related_unix_group = unix_group
                        break
                else:
                    output += self.run(
                        (
                            "rm", filename
                        )
                    )
                if related_unix_group:
                    del project_dictionary[related_unix_group]
            for project in project_dictionary.values():
                project_dir_link = os.path.join(self.home_dir, project.unix_group)
                self.run(("ln", "-s", project.project_dir, project_dir_link))

        output += self.run(
            (
                "usermod", "-G", ",".join(posix_group_list), self.login,
            )
        )

        return output

    def delete(self):
        """
        Removes the POSIX user from the database

        :return: None
        """
        from .posix_group import PosixGroup
        if self.login is not None and self.home_dir is not None:
            available_user = self.check_user_for_update()
            if available_user is not None:
                primary_gid = available_user.gid
                self.run(('userdel', '-rf', available_user.login))
                posix_groups = filter(lambda group: group.gid == primary_gid, PosixGroup.get_posix_groups())
                for group in posix_groups:
                    self.run(('groupdel', group.name))
        self._delete_user_from_database()

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
        available_logins = [posix_user.login for posix_user in self.get_posix_users()]
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

    def _update_database_info(self):
        """
        When the PosixUser gives the user new login and home directory, this method updates such values.
        """
        if self.entity is not None and not self.command_emulation:
            user_model_provider = UserProvider()
            user_model = user_model_provider.unwrap_entity(self.entity)
            user_model.unix_group = self.login
            user_model.home_dir = self.home_dir
            user_model.save()

    def _delete_user_from_database(self):
        """
        When the PosixUser deletes the user, this method deletes it from the database.
        """
        if self.entity is not None and not self.command_emulation:
            user_model_provider = UserProvider()
            user_model = user_model_provider.unwrap_entity(self.entity)
            user_model.delete()
