from core.entity.entity_readers.model_reader import ModelReader

from .rectangular_roi_provider import RectangularRoiProvider


class RectangularRoiReader(ModelReader):
    """
    Finds information about a given rectangular ROI from the database and sends it to the ROI provider
    """

    _entity_model_class = "roi.models.RectangularRoi"

    _entity_provider = RectangularRoiProvider()
