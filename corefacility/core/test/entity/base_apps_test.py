from django.utils.module_loading import import_string

from core.test.entity_set.base_test_class import BaseTestClass


class BaseAppsTest(BaseTestClass):
    """
    Contains module and entry point assertions
    """

    def assertModule(self, actual_module, expected_module, msg):
        """
        Asserts that two corefacility modules are the same

        :param actual_module: the actual module
        :param expected_module: the expected module
        :param msg: message to display when they are not the same
        :return: nothing
        """
        self.assertIs(actual_module, expected_module, msg + ". Modules are not the same")
        self.assertIsNotNone(actual_module.uuid, msg + ". UUID was not successfully loaded")
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
