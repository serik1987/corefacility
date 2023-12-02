from ru.ihna.kozhukhov.core_application.entity.entity_sets.log_set import LogSet
from .auto_admin_object import AutoAdminObject
from .posix_user import PosixUser


class PosixConnector(AutoAdminObject):
    """
    Another actions with POSIX users and groups

    Defines actions that can't be attributed to a particular POSIX user or POSIX group
    """

    log = None
    """ The log attached """

    def __init__(self, log_id=None):
        """
        :param log_id: ID of the attached corefacility log or None if no log was attached
        """
        super().__init__()
        if log_id is not None:
            self.log = LogSet().get(log_id)

    def update_connections(self, ids):
        """
        Updates connections between particular POSIX users and POSIX groups
        :param ids: IDs for the related corefacility users.
        """
        for entity_id in ids:
            posix_user = PosixUser(entity_id)
            posix_user.command_emulation = self.command_emulation
            posix_user.log = self.log
            posix_user.update_supplementary_groups()
            posix_user.copy_command_list(self)
