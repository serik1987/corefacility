from parameterized import parameterized

from core.test.entity_set.base_test_class import BaseTestClass
from core.test.data_providers.entity_sets import filter_data_provider
from imaging.tests.data_providers.entity_objects import MapSetObject

from roi.tests.entity_objects.pinwheel_set_object import PinwheelSetObject

def general_filter():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 59, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 60, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (3, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (-1, 7, 1), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (0, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (6, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (7, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (8, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 2, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 3, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 4, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 59, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 60, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (100, 200, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, None, None), BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 59, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),
    ]


def map_filter():
    return filter_data_provider(
        range(6),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

            (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        ]
    )


class TestPinwheelSet(BaseTestClass):
    """
    Provides testing routines for the pinwheel set
    """

    _map_set_object = None
    _pinwheel_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._map_set_object = MapSetObject()
        cls._pinwheel_set_object = PinwheelSetObject(cls._map_set_object.clone())

    def setUp(self):
        super().setUp()
        self._container = self._pinwheel_set_object.clone()
        self.initialize_filters()

    @parameterized.expand(general_filter())
    def test_basic(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(map_filter())
    def test_map_filter(self, map_index, *args):
        imaging_map = self._map_set_object[map_index]
        self.apply_filter("map", imaging_map)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)


del BaseTestClass
