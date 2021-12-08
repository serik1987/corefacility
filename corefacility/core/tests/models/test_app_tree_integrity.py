from django.test import TestCase
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from core.models import Module, EntryPoint
from core.models.enums import EntryPointType
from core.tests.data_providers.default_applications_provider import get_default_applications_provider


class TestAppTreeIntegrity(TestCase):

    LANGUAGES = {
        "ru": "ru-RU",
        "en": "en-GB",
    }

    def test_app_tree_integrity(self):
        app_data = get_default_applications_provider()
        self.check_app_leaf_integrity(None, "core", app_data)

    def check_app_leaf_integrity(self, entry_point, alias, app_data):
        app_model = Module.objects.get(parent_entry_point=entry_point, alias=alias)
        try:
            app_class = import_string(app_model.app_class)
        except ImportError:
            self.fail("Error in '%s': the app_model property doesn't contain a valid name of the App module class" %
                      alias)
        app_object = app_class()
        another_app_object = app_class()
        self.assertIs(app_object, another_app_object, "Error in '%s': the App class is not a singleton" % alias)
        self.assertIsInstance(app_object, app_class,
                              "Error in '%s': the App object must be an instance of App class" % alias)

        # parent entry point test
        parent_entry_point_model = app_model.parent_entry_point
        if parent_entry_point_model is None:
            self.assertEquals(alias, "core",
                              "Error in '%s': only 'core' module exist without attachment to the entry point")
            self.assertIsNone(app_object.get_parent_entry_point(),
                              "Error in '%s': 'get_parent_entry_point is not attached")
        else:
            self.assertEquals(parent_entry_point_model.alias, app_object.get_parent_entry_point().get_alias(),
                              "Error in '%s': Database integrity check fails for parent entry point" % alias)

        # Module alias test
        self.assert_module_property_consistency(alias, app_model, "alias", app_object, "get_alias")
        self.assertIn(app_object.get_alias(), app_data,
                      "Error in '%s': The application was found in the database but absent in test data")

        # Module name test
        self.assert_module_property_consistency(alias, app_model, "name", app_object, "get_name")
        for lang_id, lang_code in self.LANGUAGES.items():
            with self.settings(LANGUAGE_CODE=lang_code):
                self.assertEquals(_(app_object.get_name()), app_data[alias]['name_' + lang_id],
                                  "Error in '%s': The application name in '%s' is not the same as expected" %
                                  (alias, lang_code))

        # Module HTML code test
        self.assert_module_property_consistency(alias, app_model, "html_code", app_object, "get_html_code")
        actual_html_code = app_object.get_html_code()
        expected_html_code = app_data[alias]['html_code']
        if expected_html_code is None:
            self.assertIsNone(actual_html_code, "Error in '%s': the module HTML code is not expected" % alias)
        else:
            self.assertHTMLEqual(expected_html_code, actual_html_code,
                                 "Error in '%s': the module HTML code is not the same as expected" % alias)

        # User settings test
        settings = app_model.user_settings
        self.assertIsInstance(settings, dict,
                              "Error in '%s': value of the user_settings column shall be automatically transformed "
                              "into dict" % alias)
        self.assertEquals(len(settings), 0,
                          "Error in '%s': by default, value of the user_settings field is an empty dict" % alias)

        # Checking whether the module is application
        self.assert_module_property_consistency(alias, app_model, "is_application", app_object, "is_application")
        self.assertEquals(app_object.is_application(), app_data[alias]['is_application'],
                          "Error in '%s': the application status is not the same as expected" % alias)

        # Checking whether the module is enabled
        self.assert_module_property_consistency(alias, app_model, "is_enabled", app_object, "is_enabled_by_default")
        self.assertEquals(app_object.is_enabled_by_default(), app_data[alias]["is_enabled"],
                          "Error in '%s': the application enability is not the same as expected" % alias)

        # Checking for all application entry points
        entry_point_models = app_model.entry_points.all()
        entry_point_objects = app_object.get_entry_points()
        self.assertEquals(len(entry_point_objects), entry_point_models.count(),
                          "Error in '%s': the number of entry points stored in the database is not the same as "
                          "number of entry points defined by 'get_entry_points' method" % alias)
        self.assertEquals(len(entry_point_objects), len(app_data[alias]['entry_points']),
                          "Error in '%s': the number of entry points is not the same as expected. See corefacility "
                          "documentation for details" % alias)
        for entry_point_alias, entry_point_object in app_object.get_entry_points().items():
            # Belonging module check....
            entry_point_model = entry_point_models.get(alias=entry_point_alias, belonging_module=app_model)
            entry_point_data = app_data[alias]['entry_points'][entry_point_alias]
            self.check_entry_point_leaf_integrity(entry_point_object, entry_point_model, entry_point_alias,
                                                  entry_point_data)

    def assert_module_property_consistency(self, module_alias, module_model, db_column, module_object, func_name):
        expected_value = getattr(module_model, db_column)
        property_func = getattr(module_object, func_name)
        try:
            actual_value = property_func()
        except NotImplementedError:
            self.fail("Error in '%s': '%s' method must be re-defined in the module App class" %
                      (module_alias, func_name))
        else:
            self.assertEquals(expected_value, actual_value,
                              "Error in '%s': '%s' property in the App class is different from that in the table" %
                              (module_alias, db_column))

    def check_entry_point_leaf_integrity(self, entry_point_object, entry_point_model, alias, app_data):
        entry_point_class = entry_point_object.__class__
        another_entry_point_object = entry_point_class()
        self.assertIs(entry_point_object, another_entry_point_object,
                      "Error in EP '%s': the entry point object is not a singleton" % alias)
        self.assertIsInstance(another_entry_point_object, entry_point_class,
                              "Error in EP '%s': the entry point object constructor doesn't construct an object of "
                              "proper type" % alias)

        # Alias testing
        self.assert_entry_point_consistency(alias, entry_point_model, "alias", entry_point_object, "get_alias")
        self.assertEquals(entry_point_model.alias, alias,
                          "Error in EP '%s': the entry point alias is not the same as expected" % alias)

        # Name testing
        self.assert_entry_point_consistency(alias, entry_point_model, "name", entry_point_object, "get_name")
        for lang_id, lang_code in self.LANGUAGES.items():
            with self.settings(LANGUAGE_CODE=lang_code):
                self.assertEquals(_(entry_point_object.get_name()), app_data['name_' + lang_id],
                                  "Error in EP '%s': EP name is not the same as expected for language %s" %
                                  (alias, lang_code))

        # Entry point type
        model_ep_type = entry_point_model.type
        object_ep_type = entry_point_object.get_type()
        self.assertEquals(model_ep_type, object_ep_type,
                          "Error in EP '%s': entry point type given in the database and in the functionality "
                          "is not the same" % alias)
        self.assertEquals(object_ep_type, app_data['type'],
                          "Error in EP '%s': entry point type is not the same as expected" % alias)

        # All modules check
        actual_modules = entry_point_model.modules.filter(parent_entry_point=entry_point_model)
        try:
            expected_modules = app_data['modules']
        except KeyError:
            self.fail("Error in EP '%s': the entry point test data doesn't contain 'modules' key" % alias)
        else:
            self.assertEquals(actual_modules.count(), len(expected_modules),
                              "Error in EP '%s': number of entry point attached modules is not the same as expected")
            for module_alias, module_data in expected_modules.items():
                self.check_app_leaf_integrity(entry_point_model, module_alias, expected_modules)

    def assert_entry_point_consistency(self, alias, ep_model, ep_field, ep_object, ep_method):
        expected_value = getattr(ep_model, ep_field)
        try:
            actual_value_func = getattr(ep_object, ep_method)
            actual_value = actual_value_func()
        except NotImplementedError:
            self.fail("Error in EP '%s': the entry point object method '%s' is purely abstract and is needed to be "
                      "implemented" % (alias, ep_method))
        except AttributeError:
            self.fail("Error in EP '%s': the entry point object method '%s' is not defined in base EntryPoint class" %
                      (alias, ep_method))
        else:
            self.assertEquals(expected_value, actual_value,
                              "Error in EP '%s': the property '%s' value is not the same in the object and in the "
                              "database" % (expected_value, actual_value))
