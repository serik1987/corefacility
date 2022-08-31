from core.test.entity.entity_objects.entity_object import EntityObject

from imaging.entity import Map
from imaging.models.enums import MapType


class MapObject(EntityObject):
    """
    Facilitates access to the Map entity for testing purpose
    """

    _entity_class = Map

    _default_create_kwargs = {
        "alias": "c022_X210",
        "type": MapType.orientation,
    }

    _default_change_kwargs = {
        "alias": "c023_X210",
        "type": MapType.direction,
    }
