import csv

from .abstract import AbstractGroup
from .exceptions import OperatingSystemGroupNotFound
from .. import CommandMaker, _check_os_posix


class PosixGroup(AbstractGroup):
    """
    Represents the group information for POSIX-compatible operating system
    """

    MAX_GROUP_NAME_LENGTH = 32
    """ Defines maximum number of characters in the group name """

    GROUP_LIST_FILE = "/etc/group"
    """ Any POSIX-compliant operating system has list of all groups stored in this file """

    GROUP_NAME_POSITION = 0
    GID_POSITION = 2
    GROUP_MEMBERS_POSITION = 3

    _initial_group_name = None
    _gid = None
    _user_list = None

    @classmethod
    def iterate(cls):
        """
        Iterates over all groups

        :return: Generator that shall be used in for loop to iterate over all POSIX groups
        """
        with open(cls.GROUP_LIST_FILE, "r") as group_list_file:
            group_list_reader = csv.reader(group_list_file, delimiter=":")
            for group_info in group_list_reader:
                group = cls(name=group_info[cls.GROUP_NAME_POSITION])
                group._registered = True
                group._gid = int(group_info[cls.GID_POSITION])
                group._initial_group_name = group.name
                group_members = group_info[cls.GROUP_MEMBERS_POSITION]
                if len(group_members) > 0:
                    group._user_list = group_members.split(",")
                else:
                    group._user_list = list()
                yield group

    @classmethod
    def find_by_gid(cls, gid):
        """
        Finds a group with a proper GID

        :param gid: A group GID
        :return: A PosixGroup which GID equals to a given one
        """
        for group in cls.iterate():
            if group.gid == gid:
                return group
        raise OperatingSystemGroupNotFound(gid)

    def __init__(self, name):
        """
        Initializes the group but doesn't add it to the operating system
        :param name: the group name
        """
        _check_os_posix()
        super().__init__(name)

    def __repr__(self):
        return "core.os.group.PosixGroup(name={name}, GID={gid}, registered={registered}, {N} users)".format(
            name=self.name,
            gid=self.gid,
            registered=self.registered,
            N=len(self.user_list) if self.user_list is not None else 0
        )

    @property
    def gid(self):
        """
        The Group Identifier (GID) or None if the group has not been added to the operating system
        """
        return self._gid

    @property
    def user_list(self):
        """
        List of logins of all group members
        """
        return self._user_list

    def create(self):
        """
        Adds the group record to the operating system

        :return: nothing
        """
        if self.registered:
            raise RuntimeError("Can't create the duplicated group")
        CommandMaker().add_command(("groupadd", "-f", self.name))
        self._registered = True
        self._initial_group_name = self._name

    def update(self):
        """
        Changes information about the group in the operating system

        :return: nothing
        """
        if not self.registered or self._initial_group_name is None:
            raise RuntimeError("To change the group name please, find the group using iterate() function")
        CommandMaker().add_command(("groupmod", "-n", self.name, self._initial_group_name))
        self._initial_group_name = self._name

    def delete(self):
        """
        Deletes the group

        :return: nothing
        """
        if not self.registered:
            raise RuntimeError("Can't delete the group if it is still not added")
        CommandMaker().add_command(("groupdel", self.name))
        self._registered = False
