import csv

from django.conf import settings

from ru.ihna.kozhukhov.core_application.entity.entity_sets.project_set import ProjectSet
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import ConfigurationProfileException
from .auto_admin_object import AutoAdminObject


class PosixGroup(AutoAdminObject):
    """
    Reading, modifying and deleting POSIX group.

    Also controls the attachment of POSIX users to the POSIX group.
    """

    POSIX_GROUP_FILE = "/etc/group"
    """ Defines POSIX configuration file where all groups are located """

    name = None
    """ Name of the POSIX group """

    NAME_POSITION = 0
    """ Position of a name within the POSIX group """

    gid = None
    """ group ID or None if we don't know """

    GID_POSITION = 2
    """ Position of the group ID """

    user_list = None
    """ List of all users or None if we don't know """

    USER_LIST_POSITION = 3
    """ Position related to the comma-separated user list """

    entity = None
    """ A Project entity related to the POSIX group or None if we don't know """

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
        else:
            self.entity = None
            self.name = name
            self.gid = gid
            if user_list is None:
                user_list = []
            self.user_list = user_list

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
