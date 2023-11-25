from .auto_admin_object import AutoAdminObject
from .posix_user import PosixUser


class PosixConnector(AutoAdminObject):
    """
    Another actions with POSIX users and groups

    Defines actions that can't be attributed to a particular POSIX user or POSIX group
    """

    log = None
    """ The log attached """

    def __init__(self, log):
        """
        :param log: The corefacility log to be attached
        """
        super().__init__()
        if log is not None:
            self.log = log

    def update_connections(self, ids):
        """
        Updates connections between particular POSIX users and POSIX groups
        :param ids: IDs for the related corefacility users.
        """
        for entity_id in ids:
            posix_user = PosixUser(entity_id)
            posix_user.command_emulation = self.command_emulation
            posix_user.update_supplementary_groups()
            if self.command_emulation:
                self._command_buffer.append(posix_user.flush_command_buffer())
