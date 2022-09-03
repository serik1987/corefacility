from parameterized import parameterized

from core.test.entity.base_test_class import BaseTestClass
from core.test.data_providers.field_value_providers import integer_provider, put_stages_in_provider
from imaging.entity import Map

from roi.tests.entity_objects.rectangular_roi_object import RectangularRoiObject


def map_provider():
    return put_stages_in_provider([
        (0, 1, None),
        (2, 1, ValueError),
        (3, 1, ValueError),
    ])


class TestRectangularRoi(BaseTestClass):
    """
    Tests the rectangular ROI.
    """

    _entity_object_class = RectangularRoiObject

    _related_map = None

    _all_maps = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._related_map = Map(alias="c022_X210", type="ori")
        cls._related_map.create()
        RectangularRoiObject.define_default_kwarg("map", cls._related_map)
        other_map = Map(alias="c022_X330", type="dir")
        other_map.create()
        new_map = Map(alias="c022_X02", type="ori")
        cls._all_maps = [cls._related_map, other_map, new_map, None]

    @parameterized.expand(integer_provider(min_value=1))
    def test_left(self, *args):
        self._test_field("left", *args, use_defaults=False, right=200, top=300, bottom=400, map=self._related_map)

    @parameterized.expand(integer_provider(min_value=1))
    def test_right(self, *args):
        self._test_field("right", *args, use_defaults=False, left=100, top=300, bottom=400, map=self._related_map)

    @parameterized.expand(integer_provider(min_value=1))
    def test_top(self, *args):
        self._test_field("top", *args, use_defaults=False, left=100, right=200, bottom=400, map=self._related_map)

    @parameterized.expand(integer_provider(min_value=1))
    def test_bottom(self, *args):
        self._test_field("bottom", *args, use_defaults=False, left=100, right=200, top=300, map=self._related_map)

    @parameterized.expand(map_provider())
    def test_map(self, map_index, updated_map_index, throwing_exception, stage):
        given_map = self._all_maps[map_index]
        updated_map = self._all_maps[updated_map_index]
        self._test_field("map", given_map, updated_map, throwing_exception, stage, use_defaults=False,
                         left=100, right=200, top=300, bottom=400)

    def _check_default_fields(self, rect_roi):
        self.assertEquals(rect_roi.left, 100, "Left border was not transmitted correctly")
        self.assertEquals(rect_roi.right, 200, "Right border was not transmitted correctly")
        self.assertEquals(rect_roi.top, 300, "Top border was not transmitted correctly")
        self.assertEquals(rect_roi.bottom, 400, "Bottom border was not transmitted correctly")
        self.assertEquals(rect_roi.map.id, self._related_map.id, "ROI map was dismissed")

    def _check_default_change(self, rect_roi):
        self.assertEquals(rect_roi.left, 150, "Left border was not changed correctly")
        self.assertEquals(rect_roi.right, 200, "Right border was not changed correctly")
        self.assertEquals(rect_roi.top, 300, "Top border was not changed correctly")
        self.assertEquals(rect_roi.bottom, 400, "Bottom border was not changed correctly")
        self.assertEquals(rect_roi.map.id, self._related_map.id, "ROI map was dismissed")


del BaseTestClass
