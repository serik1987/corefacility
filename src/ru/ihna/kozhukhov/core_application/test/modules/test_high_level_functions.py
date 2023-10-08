from django.test import TestCase
from parameterized import parameterized

from ..data_providers.module_providers import module_provider, entry_point_provider, modules_method_provider


class TestHighLevelFunctions(TestCase):

    @staticmethod
    def _apply_is_enabled_filter(is_enabled, expected_module_list):
        if is_enabled:
            new_module_list = set()
            for expected_module_class in expected_module_list:
                if expected_module_class().is_enabled:
                    new_module_list.add(expected_module_class)
                expected_module_class.reset()
            expected_module_list = new_module_list
        else:
            expected_module_list = set(expected_module_list)
        return expected_module_list

    def setUp(self):
        for module_info in module_provider():
            module_info[0].reset()
        for entry_point_info in entry_point_provider():
            entry_point_info['entry_point'].reset()

    @parameterized.expand(modules_method_provider())
    def test_modules_method(self, is_enabled, entry_point_class, expected_module_list):
        """
        Tests the modules() method
        """
        expected_module_list = self._apply_is_enabled_filter(is_enabled, expected_module_list)
        for module in entry_point_class().modules(is_enabled):
            self.assertEquals(module.state, "loaded", "The module shall be properly loaded")
            self.assertIn(module.__class__, expected_module_list,
                          "The iterated modules must be within the expected module list")
            expected_module_list.remove(module.__class__)
        self.assertEquals(expected_module_list, set(),
                          "All expected modules shall be mentioned during the iteration")

    @parameterized.expand(modules_method_provider())
    def test_module_method(self, is_enabled, entry_point_class, expected_module_list):
        """
        Tests the module() method
        """
        expected_module_list = self._apply_is_enabled_filter(is_enabled, expected_module_list)
        for module in expected_module_list:
            module_alias = module().get_alias()
            module = entry_point_class().module(module_alias, is_enabled)
            self.assertEquals(module.state, "loaded", "The module must be loaded")
            self.assertEquals(module.alias, module_alias, "The module alias must be defined")

    @parameterized.expand(modules_method_provider())
    def test_widgets_method(self, is_enabled, entry_point_class, expected_module_list):
        """
        Tests the widgets() method
        """
        expected_module_list = self._apply_is_enabled_filter(is_enabled, expected_module_list)
        expected_module_info = {}
        for expected_module_class in expected_module_list:
            expected_module = expected_module_class()
            if not expected_module.is_application:
                expected_module_info[expected_module.uuid] = {
                    "alias": expected_module.alias,
                    "name": expected_module.get_entity_class_name(),
                    "html_code": expected_module.html_code
                }
        expected_module_number = len(expected_module_info)
        actual_module_number = 0
        for uuid, alias, name, html_code in entry_point_class().widgets(is_enabled):
            self.assertIn(uuid, expected_module_info, "The uuid retrieved must be within the list of expected UUIDs")
            self.assertEquals(alias, expected_module_info[uuid]['alias'],
                              "The module alias must be retrieved correctly")
            self.assertEquals(name, expected_module_info[uuid]['name'],
                              "The module name must be retrieved correctly")
            self.assertEquals(html_code, expected_module_info[uuid]['html_code'],
                              "The module html code must be retrieved correctly")
            actual_module_number += 1
        self.assertEquals(actual_module_number, expected_module_number,
                          "Some corefacility modules were not found in the module list")
