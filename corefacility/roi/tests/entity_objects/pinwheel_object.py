from core.test.entity.entity_objects.entity_object import EntityObject
from roi.entity import Pinwheel


class PinwheelObject(EntityObject):
    """
    Facilitates an access to the pinwheel center for testing purpose
    """

    _entity_class = Pinwheel

    _default_create_kwargs = {"x": 141, "y": 210}

    _default_change_kwargs = {"x": 400, "y": 500}
