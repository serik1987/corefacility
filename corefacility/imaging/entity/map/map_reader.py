from core.entity.entity_readers.model_reader import ModelReader

from .map_provider import MapProvider


class MapReader(ModelReader):
    """
    Retrieves information about the imaging map from the database and saves it to the hard disk drive.
    """

    _entity_model_class = "imaging.models.Map"

    _entity_provider = MapProvider()
