from .entity_set import EntitySet
from ..entity_exceptions import EntityNotFoundException
from ..entity_readers.log_record_reader import LogRecordReader


class LogRecordSet(EntitySet):
    """
    Connects particular log record with some log record reader
    """

    _entity_name = "Log record"

    _entity_class = "core.entity.log_record.LogRecord"

    _entity_reader_class = LogRecordReader

    _entity_filter_list = {
        "log": ["core.entity.log.Log", None]
    }

    def get(self, lookup):
        """
        Finds the entity by id
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.

        Entity aliases are not supported for the log records

        The function must be executed in one request.

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        if isinstance(lookup, str):
            raise EntityNotFoundException()
        else:
            return super().get(lookup)
