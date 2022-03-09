from django.utils.translation import gettext_lazy as _

from core.entity.entity_sets.entity_set import EntitySet

from .rectangular_roi_reader import RectangularRoiReader


class RectangularRoiSet(EntitySet):
    """
    Manages list of rectangular ROIs stored in the database
    """

    _entity_name = _("Rectangular ROI")

    _entity_class = "roi.entity.RectangularRoi"

    _entity_reader_class = RectangularRoiReader

    _entity_filter_list = {
        "map": ("imaging.entity.Map", None),
    }
