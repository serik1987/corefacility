import csv
import os
import re

from django.conf import settings

from ru.ihna.kozhukhov.core_application.entity.entity_sets.project_set import ProjectSet
from ru.ihna.kozhukhov.core_application.entity.entity_sets.user_set import UserSet
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import ConfigurationProfileException, \
    RetryCommandAfterException
from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.project_provider import ProjectProvider
from .auto_admin_object import AutoAdminObject
from .posix_user import PosixUser


class PosixGroup(AutoAdminObject):
    """
    Reading, modifying and deleting POSIX group.

    Also controls the attachment of POSIX users to the POSIX group.
    """

    POSIX_GROUP_FILE = "/etc/group"
    """ Defines POSIX configuration file where all groups are located """

    POSIX_GROUP_NAME_MAXSIZE = 8
    """ Maximum number of symbols inside the POSIX group """

    MAXIMUM_TRIAL_NUMBER = 1_000
    """ Maximum number of attempts to try before switching to the new format """

    ENUMERATED_GROUP_TEMPLATE = re.compile(r"^(.+?)(\d+)$")
    """ Template for enumerated groups, i.e., group1, group2, ..."""

    NUMBERED_GROUP_TEMPLATE = re.compile(r"^(\d+)$")
    """ Template for numbered groups, i.e., 1, 2, 3, ... """

    NAME_POSITION = 0
    """ Position of a name within the POSIX group """

    GID_POSITION = 2
    """ Position of the group ID """

    USER_LIST_POSITION = 3
    """ Position related to the comma-separated user list """

    PROJECT_DIR_PERMISSIONS = "02770"
    """ Permissions for the newly created project directory """

    name = None
    """ Name of the POSIX group """

    gid = None
    """ group ID or None if we don't know """

    user_list = None
    """ List of all users or None if we don't know """

    entity = None
    """ A Project entity related to the POSIX group or None if we don't know """

    project_dir = None
    """ Directory where common project files are located """

    @classmethod
    def get_posix_groups(cls):
        """
        Lists all available POSIX groups
        :return: list of all POSIX groups
        """
        cls._static_objects = []
        with open(cls.POSIX_GROUP_FILE, 'r') as posix_group_file:
            posix_group_reader = csv.reader(posix_group_file, delimiter=':')
            for posix_group_info in posix_group_reader:
                posix_group = cls(
                    name=posix_group_info[cls.NAME_POSITION],
                    gid=posix_group_info[cls.GID_POSITION],
                    user_list=posix_group_info[cls.USER_LIST_POSITION].split(',')
                )
                cls._static_objects.append(posix_group)
        return cls._static_objects

    def __init__(self, entity=None, name=None, gid=None, user_list=None):
        """
        Initializes the object.

        :param entity: name of the Project entity that relates to the POSIX group
        :param name: the POSIX group name
        :param gid: GID of the POSIX group
        :param user_list: list of POSIX login for all users containing in the group.
        """
        super().__init__()
        if entity is None and name is None:
            raise ValueError("either group name or related entity must be specified")
        if entity is not None and not settings.CORE_MANAGE_UNIX_GROUPS:
            raise ConfigurationProfileException(settings.CONFIGURATION)
        if isinstance(entity, int):
            entity = ProjectSet().get(entity)
        if entity is not None:
            self.entity = entity
            self.name = entity.unix_group
            self.project_dir = entity.project_dir
            self.gid = None
            self.user_list = []
            self.log = self.entity.log
        else:
            self.entity = None
            self.name = name
            self.gid = gid
            self.project_dir = None
            if user_list is None:
                user_list = []
            self.user_list = user_list
            self.log = None

    @property
    def project_id(self):
        """
        ID of the related project
        """
        if self.entity is None:
            return None
        else:
            return self.entity.id

    def __str__(self):
        return "PosixGroup(name={name}, gid={gid}, user_list={user_list}, project_id={project_id})".format(
            name=self.name,
            gid=self.gid,
            user_list=";".join(self.user_list),
            project_id=self.project_id,
        )

    def create(self):
        """
        Creates new POSIX group for a particular project
        :return: the output results for all commands.
        """
        output = ""
        if self.entity is None:
            raise RuntimeError("The POSIX group can be created for a particular project only.")
        governor_id = self.entity.governor.id
        governor = UserSet().get(governor_id)
        if governor.unix_group is None:
            raise RetryCommandAfterException()
        user_list = set()
        for user in self.entity.root_group.users:
            posix_user = PosixUser(user)
            if posix_user.check_user_for_update() is None:
                output += posix_user.create()
            user_list.add((posix_user.login, posix_user.home_dir))
        if self.name is None or self.project_dir is None:
            self._generate_unix_group_name()
            self.project_dir = self._generate_project_dir()
        owner = "%s:%s" % (governor.unix_group, self.name)
        output += self.run(("groupadd", self.name))
        output += self.run(("mkdir", self.project_dir))
        output += self.run(("chown", owner, self.project_dir))
        output += self.run(("chmod", self.PROJECT_DIR_PERMISSIONS, self.project_dir))
        output += self.run(("usermod", "-aG", self.name, settings.CORE_WORKER_PROCESS_USER))
        for user in user_list:
            login, home_dir = user
            output += self.run(("usermod", "-aG", self.name, login))
            project_dir_link = os.path.join(home_dir, self.name)
            output += self.run(("ln", "-s", self.project_dir, project_dir_link))
        self._update_database_info()
        return output

    def check_group_for_update(self):
        """
        Checks whether the group is valid POSIX group

        :return: PosixGroup instance related to the POSIX group found in the /etc/group or None if no such group found.
        """
        if self.name is None or self.project_dir is None:
            raise RetryCommandAfterException()
        available_posix_groups = filter(lambda group: group.name == self.name, self.get_posix_groups())
        for posix_group in available_posix_groups:
            return posix_group
        return None

    def _find_all_users(self):
        """
        Looks for all users attached to a given project

        :return: list of all attached users
        """
        user_list = list()
        user_ids = set()
        for group, _ in self.entity.permissions:
            if group is None:
                continue
            for user in group.users:
                if user.id not in user_ids:
                    user_list.append(user)
                    user_ids.add(user.id)
        return user_list

    def exclude_all_users(self):
        """
        Excludes all users related to a particular corefacility project from the UNIX group.

        :return: POSIX output.
        """
        output = ""
        user_list = self._find_all_users()

        for user in user_list:
            posix_user = PosixUser(user)
            posix_user.command_emulation = self.command_emulation
            posix_user.log = self.log
            output += posix_user.update_supplementary_groups(exclude=self.name)
            posix_user.copy_command_list(self)

        return output

    def update_alias(self):
        """
        Updates the name of the POSIX group and the home directory according to the project alias.
        """
        output = ""
        available_group = self.check_group_for_update()
        if available_group is None:
            return self.create()

        old_group_name = self.name
        old_project_dir = self.project_dir
        self._generate_unix_group_name()
        self.project_dir = self._generate_project_dir()
        output += self.run(("groupmod", "-n", self.name, old_group_name))
        output += self.run(("mv", old_project_dir, self.project_dir))
        for user in self._find_all_users():
            if not user.home_dir:
                raise RetryCommandAfterException()
            for filename in os.listdir(user.home_dir):
                fullname = os.path.join(user.home_dir, filename)
                if not os.path.islink(fullname):
                    continue
                target = os.readlink(fullname)
                if target == old_project_dir:
                    new_link_name = os.path.join(user.home_dir, self.name)
                    output += self.run(("rm", fullname))
                    output += self.run(("ln", "-s", self.project_dir, new_link_name))
        self._update_database_info()

        return output

    def update_root_group(self, old_root_group_id=None):
        """
        Updates the group-user relationships according to the changed root group.

        :param old_root_group_id: ID of the old root group. This is a required parameter.
        """
        available_group = self.check_group_for_update()
        if not available_group:
            self.create()
            return
        if old_root_group_id is None:
            raise ValueError("The old_root_group_id argument was not passed to the update_root_group")

        user_dictionary = dict()
        excluded_users = set()
        included_users = set()
        from ru.ihna.kozhukhov.core_application.entity.group import GroupSet
        old_root_group = GroupSet().get(old_root_group_id)
        for user in old_root_group.users:
            excluded_users.add(user.id)
            user_dictionary[user.id] = user
        for user in self.entity.root_group.users:
            included_users.add(user.id)
            user_dictionary[user.id] = user
        changed_users = excluded_users ^ included_users  # Users that are either excluded or included.

        for user_id in changed_users:
            user = user_dictionary[user_id]
            posix_user = PosixUser(user)
            posix_user.command_emulation = self.command_emulation
            posix_user.log = self.log
            posix_user.update_supplementary_groups()
            posix_user.copy_command_list(self)
        from ru.ihna.kozhukhov.core_application.entity.user import UserSet
        governor = UserSet().get(self.entity.governor.id)
        if self.project_dir and governor.unix_group:
            self.run(("chown", governor.unix_group, self.project_dir))

    def delete(self):
        """
        Removes the POSIX group and detaches all its POSIX users.
        """
        output = ""
        if self.name is not None and self.project_dir is not None:
            self.check_group_for_update()
            output += self.exclude_all_users()
            output += self.run(("rm", "-rf", self.project_dir))
            output += self.run(("groupdel", self.name))
        self._delete_group_from_database()
        return output

    def _generate_unix_group_name(self):
        """
        Generates the UNIX group name
        """
        desired_group_name = self.entity.alias[:self.POSIX_GROUP_NAME_MAXSIZE]
        group_list = [group.name for group in self.get_posix_groups()]
        while desired_group_name in group_list:
            enumerated_group_matches = self.ENUMERATED_GROUP_TEMPLATE.match(desired_group_name)
            numbered_group_matches = self.NUMBERED_GROUP_TEMPLATE.match(desired_group_name)
            if numbered_group_matches is not None:
                group_index = int(desired_group_name)
                desired_group_name = str(group_index + 1)
                if group_index >= int("9" * self.POSIX_GROUP_NAME_MAXSIZE):
                    raise RuntimeError("Too many POSIX groups inside the operating system. Decline their number")
            elif enumerated_group_matches is not None:
                group_prefix = enumerated_group_matches[1]
                group_number = int(enumerated_group_matches[2])
                if group_number >= self.MAXIMUM_TRIAL_NUMBER:
                    desired_group_name = "0"
                else:
                    desired_group_name = "%s%d" % (group_prefix, group_number+1)
            else:
                desired_group_name += "0"
            if len(desired_group_name) > self.POSIX_GROUP_NAME_MAXSIZE:
                desired_group_name = desired_group_name[1:]
        self.name = desired_group_name

    def _generate_project_dir(self):
        """
        Creates new name for the project directory, if old one does not exist.

        :return: a string containing name of the new project directory
        """
        return os.path.join(settings.CORE_PROJECT_BASEDIR, self.name)

    def _update_database_info(self):
        """
        Updates the unix_group and home_dir columns in the core_application_project database table
        """
        if self.entity is not None and not self.command_emulation:
            project_provider = ProjectProvider()
            project_model = project_provider.unwrap_entity(self.entity)
            project_model.unix_group = self.name
            project_model.project_dir = self.project_dir
            project_model.save()

    def _delete_group_from_database(self):
        """
        Removes an entry from the core_application_project database entry
        """
        if self.entity is not None and not self.command_emulation:
            project_provider = ProjectProvider()
            project_model = project_provider.unwrap_entity(self.entity)
            project_model.delete()
