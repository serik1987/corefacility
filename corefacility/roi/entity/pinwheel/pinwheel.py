from core.entity.entity import Entity
from core.entity.entity_fields.entity_field import EntityField
from core.entity.entity_fields.related_entity_field import RelatedEntityField

from .pinwheel_set import PinwheelSet
from .pinwheel_provider import PinwheelProvider


class Pinwheel(Entity):
    """
    Represents a single pinwheel
    """

    _entity_set_class = PinwheelSet

    _required_fields = ["x", "y", "map"]

    _entity_provider_list = [PinwheelProvider()]

    _public_field_description = {
        "x": EntityField(int, min_value=0, description="Pinwheel abscissa"),
        "y": EntityField(int, min_value=0, description="Pinwheel ordinate"),
        "map": RelatedEntityField("imaging.entity.Map", description="Related map"),
    }
