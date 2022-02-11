from core.models import EntryPoint

from .model_reader import ModelReader
from ..entity_providers.model_providers.entry_point_provider import EntryPointProvider


class EntryPointReader(ModelReader):
    """
    Reads the entry point information from the database and sends it to the EntryPointProvider
    """

    _entity_model_class = EntryPoint

    _entity_provider = EntryPointProvider()
