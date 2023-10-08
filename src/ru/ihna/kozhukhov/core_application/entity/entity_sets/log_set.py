from datetime import datetime

from .entity_set import EntitySet
from ...exceptions.entity_exceptions import EntityNotFoundException
from ..readers.log_reader import LogReader


class LogSet(EntitySet):
    """
    Declares all facilities for log looking
    """

    _entity_name = "Log"

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.log.Log"

    _entity_reader_class = LogReader

    _entity_filter_list = {
        "request_date_from": [datetime, None],
        "request_date_to": [datetime, None],
        "ip_address": [str, None],
        "user": ["ru.ihna.kozhukhov.core_application.entity.user.User", None],
        "is_anonymous": [bool, None],
        "is_success": [bool, None],
        "is_fail": [bool, None],
    }

    def get(self, lookup):
        """
        Finds the entity by id or alias
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity alias is a unique string name assigned by the user during the entity post.

        The function must be executed in one request

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        if isinstance(lookup, str):
            raise EntityNotFoundException()
        else:
            return super().get(lookup)

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
