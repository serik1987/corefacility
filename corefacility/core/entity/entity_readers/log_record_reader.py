from core.models import LogRecord as LogRecordModel

from .model_reader import ModelReader
from ..entity_providers.model_providers.log_record_provider import LogRecordProvider


class LogRecordReader(ModelReader):
    """
    Retrieves the log record information from the database and organizes it in form of the LogRecord entity.
    """

    _entity_model_class = LogRecordModel

    _entity_provider = LogRecordProvider()
