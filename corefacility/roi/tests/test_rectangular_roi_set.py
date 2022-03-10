from parameterized import parameterized

from core.test.data_providers.entity_sets import filter_data_provider
from core.test.entity_set.base_test_class import BaseTestClass

from imaging.tests.entity_objects.map_set_object import MapSetObject

from .entity_objects.rectangular_roi_set_object import RectangularRoiSetObject


def general_search_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


def map_filter_provider():
    return filter_data_provider(
        range(6),
        general_search_provider()
    )


class TestRectangularRoiSet(BaseTestClass):
    """
    Tests searching facilities across the rectangular ROI.
    """

    _map_set_object = None
    _rectangular_roi_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._map_set_object = MapSetObject()
        cls._rectangular_roi_set_object = RectangularRoiSetObject(cls._map_set_object.clone())

    def setUp(self):
        super().setUp()
        self._container = self._rectangular_roi_set_object.clone()
        self.initialize_filters()

    @parameterized.expand(general_search_provider())
    def test_general_search(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(map_filter_provider())
    def test_map_filter(self, map_index, *args):
        current_map = self._map_set_object[map_index]
        self.apply_filter("map", current_map)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)
