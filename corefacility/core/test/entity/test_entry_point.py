from parameterized import parameterized_class

from core.test.data_providers.module_providers import entry_point_provider
from .base_apps_test import BaseAppsTest


@parameterized_class(entry_point_provider())
class TestEntryPoint(BaseAppsTest):
    """
    Tests entry points
    """

    entry_point = None
    expected_module_list = None
    base_module_class = None

    def test_singleton(self):
        """
        Checks whether the entry point is singleton
        """
        ep1 = self.entry_point()
        ep2 = self.entry_point()
        self.assertIs(ep1, ep2, "The entry point is not singleton")
