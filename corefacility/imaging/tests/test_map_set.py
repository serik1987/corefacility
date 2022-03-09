from parameterized import parameterized

from core.test.entity_set.base_test_class import BaseTestClass

from .entity_objects.map_set_object import MapSetObject


class TestMapSet(BaseTestClass):
    """
    Provides the map set testing
    """

    _imaging_map_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._imaging_map_object = MapSetObject()

    def setUp(self):
        super().setUp()
        self._container = self._imaging_map_object.clone()

    @parameterized.expand([
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 5, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ALIAS, "c022_X210", BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "c022_X100", BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "c022_X300", BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (2, 4, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (2, 4, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, None, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (10, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
    ])
    def test_all_access_features(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)


del BaseTestClass
