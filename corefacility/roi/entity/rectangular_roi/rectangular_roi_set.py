from django.utils.translation import gettext_lazy as _

from core.entity.entity_exceptions import EntityNotFoundException
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

    def get(self, lookup):
        """
        Finds the entity by id or alias
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity alias is a unique string name assigned by the user during the entity post.

        The function must be executed in one request

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        if isinstance(lookup, str):
            raise EntityNotFoundException()
        return super().get(lookup)
