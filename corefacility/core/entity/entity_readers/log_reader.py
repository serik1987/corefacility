from core.models import Log as LogModel

from .model_reader import ModelReader
from ..entity_providers.model_providers.log_provider import LogProvider


class LogReader(ModelReader):
    """
    Retrieves the log information from the database and saves it to the hard disk drive
    """

    _entity_model_class = LogModel

    _entity_provider = LogProvider()
