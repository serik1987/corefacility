from .entity_set import EntitySet


class LogRecordSet(EntitySet):
    """
    Connects particular log record with some log record reader
    """

    _entity_name = "Log record"

    _entity_class = "core.entity.log_record.LogRecord"

    _entity_reader_class = None  # TO-DO: define a proper entity reader

    _entity_filter_list = {
        "log": ["core.entity.log.Log", None]
    }
