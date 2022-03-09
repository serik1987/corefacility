from core.test.entity.entity_objects.entity_object import EntityObject

from roi.entity import RectangularRoi


class RectangularRoiObject(EntityObject):
    """
    Represents an auxiliary rectangular ROI object that facilitates ROI access for testing purpose
    """

    _entity_class = RectangularRoi

    _default_create_kwargs = {"left": 100, "right": 200, "top": 300, "bottom": 400}

    _default_change_kwargs = {"left": 150}
