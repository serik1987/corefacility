from datetime import datetime

from .entity_set import EntitySet
from ..entity_readers.log_reader import LogReader


class LogSet(EntitySet):
    """
    Declares all facilities for log looking
    """

    _entity_name = "Log"

    _entity_class = "core.entity.log.Log"

    _entity_reader_class = LogReader

    _entity_filter_list = {
        "request_date_from": [datetime, None],
        "request_date_to": [datetime, None],
        "ip_address": [str, None],
        "user": ["core.entity.user.User", None],
    }

    def rotate(self, up_to: datetime) -> str:
        """
        Rotates all logs earlier than this particular time. Rotation means:
        1) All log information will be converted to string
        2) After conversion such information will be deleted from the database

        The operation will be run given that the only entity provider connected
        to this log class is database entity provider

        :param up_to: such a particular time
        :return: str a string containing all information about the rotated logs
        """
        raise NotImplementedError("TO-DO: LogSet.rotate")
