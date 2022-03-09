from core.entity.entity_readers.model_reader import ModelReader

from .pinwheel_provider import PinwheelProvider


class PinwheelReader(ModelReader):
    """
    Retireves information about pinwheel centers from the database and passes it to the Pinwheel entity
    """

    _entity_model_class = "roi.models.Pinwheel"

    _entity_provider = PinwheelProvider()
