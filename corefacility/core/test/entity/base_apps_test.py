from uuid import UUID
from django.utils.module_loading import import_string

from core.entity.entity_sets.corefacility_module_set import CorefacilityModuleSet
from core.entity.entry_points.entry_point_set import EntryPointSet

from core.test.entity_set.base_test_class import BaseTestClass


class BaseAppsTest(BaseTestClass):
    """
    Contains module and entry point assertions.

    IMPORTANT: During the testing the UUID of the tested module is not the same as UUID of the module stored in the
    database. It's OK because testing database is not the same thing as production database
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        module_set = CorefacilityModuleSet()
        for _ in module_set:
            pass

        entry_point_set = EntryPointSet()
        for _ in entry_point_set:
            pass

    def assertModule(self, actual_module, expected_module, msg):
        """
        Asserts that two corefacility modules are the same

        :param actual_module: the actual module
        :param expected_module: the expected module
        :param msg: message to display when they are not the same
        :return: nothing
        """
        self.assertIs(actual_module, expected_module, msg + ". Modules are not the same")
        self.assertIsInstance(actual_module.uuid, UUID, msg + ". Module's UUID is not an instance of the UUID class")
        self.assertEquals(actual_module._uuid, expected_module.uuid, msg + ". Module's UUID is not the same")
        self.assertEquals(actual_module._alias, expected_module.alias, msg + ". Unexpected module alias")
        self.assertEquals(actual_module._name, expected_module.name, msg + ". Unexpected module name")
        self.assertEquals(actual_module._html_code, expected_module.html_code, msg + ". Unexpected module HTML code")
        self.assertEquals(actual_module._app_class, expected_module.app_class, msg + ". Unexpected module app class")
        expected_class = import_string(actual_module.app_class)
        actual_class = actual_module.__class__
        self.assertIs(actual_class, expected_class, msg + ". Module app_class inconsistency")
        self.assertEquals(actual_module.user_settings, expected_module.user_settings,
                          msg + ". User settings are not the same")
        self.assertEquals(actual_module._is_application, expected_module.is_application,
                          msg + ". Module application status inconsistency")
        self.assertEquals(actual_module._is_enabled, expected_module.is_enabled,
                          msg + ". The module enability status is not the same")
