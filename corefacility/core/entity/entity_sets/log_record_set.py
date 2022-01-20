from .entity_set import EntitySet
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
