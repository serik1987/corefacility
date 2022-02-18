from parameterized import parameterized

from core import App as CoreApp
from imaging import App as ImagingApp

from core.test.data_providers.module_providers import entry_point_provider
from core.test.data_providers.entity_sets import filter_data_provider
from .base_apps_test import BaseAppsTest
from .entity_objects.entry_point_set_object import EntryPointSetObject


def entry_point_classes_provider():
    return [(ep_info['entry_point'],) for ep_info in entry_point_provider()]


def is_parent_root_provider():
    return filter_data_provider(
        (True, False),
        [
            (BaseAppsTest.TEST_COUNT, None, BaseAppsTest.POSITIVE_TEST_CASE),
            (BaseAppsTest.TEST_ITERATION, None, BaseAppsTest.POSITIVE_TEST_CASE),
        ]
    )


def parent_module_filter_provider():
    return filter_data_provider(
        (CoreApp(), ImagingApp()),
        [
            (BaseAppsTest.TEST_COUNT, None, BaseAppsTest.POSITIVE_TEST_CASE),
            (BaseAppsTest.TEST_ITERATION, None, BaseAppsTest.POSITIVE_TEST_CASE),
        ]
    )


class TestEntryPoint(BaseAppsTest):
    """
    Tests entry points
    """

    _entry_point_set_object = None

    @classmethod
    def setUpTestData(cls):
        """
        This method will be executed before all tests and makes common test pre-conditions

        :return: nothing
        """
        super().setUpTestData()
        cls._entry_point_set_object = EntryPointSetObject()

    def setUp(self):
        """
        This method will be executed before each test and completes making the test pre-conditions

        :return: nothing
        """
        self._container = self._entry_point_set_object.clone()
        self._container.sort()
        self.initialize_filters()

    @parameterized.expand(entry_point_classes_provider())
    def test_singleton(self, entry_point):
        """
        Checks whether the entry point is singleton
        """
        ep1 = entry_point()
        ep2 = entry_point()
        self.assertIs(ep1, ep2, "The entry point is not singleton")

    @parameterized.expand([
        (BaseAppsTest.TEST_COUNT, None, BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_ITERATION, None, BaseAppsTest.POSITIVE_TEST_CASE),

        (BaseAppsTest.TEST_FIND_BY_INDEX, -1, BaseAppsTest.NEGATIVE_TEST_CASE),
        (BaseAppsTest.TEST_FIND_BY_INDEX, 0, BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_FIND_BY_INDEX, 4, BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_FIND_BY_INDEX, 5, BaseAppsTest.NEGATIVE_TEST_CASE),

        (BaseAppsTest.TEST_FIND_BY_ID, -1, BaseAppsTest.NEGATIVE_TEST_CASE),

        (BaseAppsTest.TEST_SLICING, (2, 4, None), BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_SLICING, (10, 20, 1), BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_SLICING, (2, 1, 1), BaseAppsTest.POSITIVE_TEST_CASE),
    ])
    def test_entry_pont_set(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(is_parent_root_provider())
    def test_filter_is_parent_root(self, is_parent_root, *args):
        self.apply_filter("parent_module_is_root", is_parent_root)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(parent_module_filter_provider())
    def test_filter_parent_module(self, parent_module, *args):
        self.apply_filter("parent_module", parent_module)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)
