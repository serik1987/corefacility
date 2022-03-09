from core.entity.entity import Entity
from core.entity.entity_fields.entity_field import EntityField
from core.entity.entity_fields.related_entity_field import RelatedEntityField

from .rectangular_roi_set import RectangularRoiSet
from .rectangular_roi_provider import RectangularRoiProvider


class RectangularRoi(Entity):
    """
    Represents a single rectangular ROI.
    """

    _entity_set_class = RectangularRoiSet

    _entity_provider_list = [RectangularRoiProvider()]

    _required_fields = ["left", "right", "top", "bottom", "map"]

    _public_field_description = {
        "left": EntityField(int, min_value=1, description="Left"),
        "right": EntityField(int, min_value=1, description="Right"),
        "top": EntityField(int, min_value=1, description="Top"),
        "bottom": EntityField(int, min_value=1, description="Bottom"),
        "map": RelatedEntityField("imaging.entity.Map", description="Imaging map"),
    }
