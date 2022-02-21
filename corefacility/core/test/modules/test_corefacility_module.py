from uuid import UUID, uuid4
from parameterized import parameterized

from core import App as CoreApp
from core.entity.entity_fields.field_managers.app_permission_manager import AppPermissionManager
from core.entity.entity_sets.corefacility_module_set import CorefacilityModuleSet
from core.entity.entry_points import EntryPoint
from core.entity.entry_points.authorizations import AuthorizationsEntryPoint

from core.test.data_providers.entity_sets import filter_data_provider
from core.test.data_providers.module_providers import module_provider, entry_point_provider
from core.test.entity.base_apps_test import BaseAppsTest
from core.test.entity.entity_objects.corefacility_module_set_object import CorefacilityModuleSetObject

ALL_ENTRY_POINT_CLASSES = [ep_info['entry_point'] for ep_info in entry_point_provider()]


def entry_point_filter_provider():
    return filter_data_provider(
        [ep_info['entry_point'] for ep_info in entry_point_provider()],
        [
            (BaseAppsTest.TEST_COUNT, None, BaseAppsTest.POSITIVE_TEST_CASE),
            (BaseAppsTest.TEST_ITERATION, None, BaseAppsTest.POSITIVE_TEST_CASE),
        ]
    )


def true_false_provider():
    return filter_data_provider(
        [True, False],
        [
            (BaseAppsTest.TEST_COUNT, None, BaseAppsTest.POSITIVE_TEST_CASE),
            (BaseAppsTest.TEST_ITERATION, None, BaseAppsTest.POSITIVE_TEST_CASE),
        ]
    )


def default_module_list_provider():
    return [
        (item['entry_point'], item['base_module_class'], item['expected_module_list'])
        for item in entry_point_provider()
    ]


def improved_entry_point_provider():
    return [(entry_point_info,) for entry_point_info in entry_point_provider()]


def property_autoload_provider():
    return [
        (module_class[0], name, default_value, use_uuid)
        for module_class in module_provider()
        for name, default_value in [
            ("uuid", "xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx"),
            ("user_settings", None),
            ("is_enabled", None)
        ]
        for use_uuid in (True, False)
    ]


def read_only_property_provider():
    return [
        (module_info[0], name, desired_class, default_value, can_be_none)
        for module_info in module_provider()
        for name, desired_class, default_value, can_be_none in (
            ("alias", str, "unknown", False),
            ("name", str, "unknown", False),
            ("html_code", str, "<div class='xss-injection'></div>", True),
            ("app_class", str, "django.test.TestCase", False),
            ("is_application", bool, False, False),
        )
    ]


def is_enabled_provider():
    return [
        (module_info[0], value)
        for module_info in module_provider()
        for value in (True, False)
    ]


def user_settings_provider():
    return [
        (module_info[0], name, value, default_value)
        for module_info in module_provider()
        for name, value, default_value in (
            ("some_integer_value", 42, 100),
            ("some_string_value", "hello", "Hello, World!"),
            ("some_boolean_value", True, False),
            ("some_float_value", 3.14, 6.42),
            ("some_none_value", None, None),
        )
    ]


class TestCorefacilityModule(BaseAppsTest):
    """
    Provides basic testing all corefacility modules as applications
    """

    _module_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._module_set_object = CorefacilityModuleSetObject()

    def setUp(self):
        self._container = self._module_set_object.clone()
        self.initialize_filters()

    @parameterized.expand(module_provider())
    def test_singleton(self, module_class):
        """
        Tests whether the module is singleton
        """
        module1 = module_class()
        module2 = module_class()
        self.assertIs(module1, module2, "The module %s  doesn't have singleton properties" % str(module_class))

    @parameterized.expand([
        (BaseAppsTest.TEST_COUNT, None, BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_ITERATION, None, BaseAppsTest.POSITIVE_TEST_CASE),

        (BaseAppsTest.TEST_FIND_BY_INDEX, -1, BaseAppsTest.NEGATIVE_TEST_CASE),
        (BaseAppsTest.TEST_FIND_BY_INDEX, 0, BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_FIND_BY_INDEX, 11, BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_FIND_BY_INDEX, 12, BaseAppsTest.NEGATIVE_TEST_CASE),

        (BaseAppsTest.TEST_SLICING, (3, 7, 1), BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_SLICING, (10, 20, 1), BaseAppsTest.POSITIVE_TEST_CASE),
        (BaseAppsTest.TEST_SLICING, (8, 7, 1), BaseAppsTest.POSITIVE_TEST_CASE),
    ])
    def test_module_set(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand([
        (True, 1),
        (False, 11)
    ])
    def test_filter_is_root_module_count(self, filter_value, module_count):
        module_set = CorefacilityModuleSet()
        module_set.is_root_module = filter_value
        with self.assertLessQueries(1):
            self.assertEquals(len(module_set), module_count,
                              "is_root_module = %s doesn't reveal proper number of modules" % filter_value)

    @parameterized.expand([(True,), (False,)])
    def test_filter_is_root_module_iteration(self, filter_value):
        self.apply_filter("is_root_module", filter_value)
        with self.assertLessQueries(1):
            self._test_all_access_features(self.TEST_ITERATION, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand(entry_point_filter_provider())
    def test_filter_by_entry_point(self, entry_point_class, *args):
        entry_point = entry_point_class()
        self.apply_filter("entry_point", entry_point)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(default_module_list_provider())
    def test_default_module_list(self, entry_point_class, base_module_class, expected_module_list):
        entry_point = entry_point_class()
        module_set = CorefacilityModuleSet()
        module_set.entry_point = entry_point
        with self.assertLessQueries(1):
            for module in module_set:
                self.assertIsInstance(module, base_module_class,
                                      "The module %s connected to the entry point %s is not an instance of %s" %
                                      (repr(module), repr(entry_point), base_module_class.__name__))
                self.assertIn(module.__class__, expected_module_list,
                              "The module %s was not found in the expected module list" % repr(module))

    @parameterized.expand(improved_entry_point_provider())
    def test_find_module_by_alias(self, entry_point_info):
        entry_point = entry_point_info['entry_point']()
        module_set = CorefacilityModuleSet()
        module_set.entry_point = entry_point
        for expected_module_class in entry_point_info['expected_module_list']:
            expected_module = expected_module_class()
            module_alias = expected_module.alias
            actual_module = module_set.get(module_alias)
            self.assertModule(actual_module, expected_module,
                              "The module %s that shall be within the list is damaged" % repr(expected_module))

    @parameterized.expand(module_provider())
    def test_find_module_by_uuid(self, expected_module_class):
        expected_module = expected_module_class()
        uuid = expected_module.uuid
        self.assertIsInstance(uuid, UUID, "The module UUID was not loaded correctly during the set up")
        module_set = CorefacilityModuleSet()
        actual_module = module_set.get(uuid)
        self.assertModule(actual_module, expected_module,
                          "The module %s that shall be within the list is damaged" % repr(expected_module))

    @parameterized.expand(true_false_provider())
    def test_find_is_enabled(self, is_enabled, *args):
        self.apply_filter("is_enabled", is_enabled)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(true_false_provider())
    def test_find_is_application(self, is_application, *args):
        self.apply_filter("is_application", is_application)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(module_provider())
    def test_initial_state(self, module_class):
        module_class.reset()
        with self.assertLessQueries(0):
            module = module_class()
            self.assertEquals(module.state, "found", "When the module is just importing its state must be FOUND")
            self.assertEquals(module.alias, module.get_alias(), "The module alias must be predefined")
            self.assertEquals(module.name, module.get_name(), "The human-readable module name must be predefined")
            if module.alias != "core":
                self.assertIsInstance(module.parent_entry_point, EntryPoint,
                                      "The module is not core and doesn't have a parent entry point")
            else:
                self.assertIsNone(module.parent_entry_point, "The core module has an entry point")
            self.assertEquals(module.html_code, module.get_html_code(), "The module HTML code is not the same")
            self.assertIsNone(module._user_settings, "The module user settings were self-generated")
            self.assertIsNone(module._is_enabled, "The module enability was not reset to the default state")
            if module.is_application:
                self.assertIsInstance(module.permissions, AppPermissionManager,
                                      "The application doeasn't have permissions that are "
                                      "instance of the AppPermissionManager")
            else:
                self.assertIsNone(module.permissions, "The module is not an application but has permissions")

    @parameterized.expand(property_autoload_provider())
    def test_property_autoload(self, module_class, name, default_value, use_uuid):
        module = module_class()
        expected_value = getattr(module, name)
        uuid = module.uuid
        module_class.reset()
        module = module_class()
        with self.assertLessQueries(0):
            null_value = getattr(module, '_' + name)
            self.assertEquals(null_value, default_value,
                              "The property %s doesn't throw its value to default set during the module reset" % name)
        with self.assertLessQueries(1):
            if use_uuid:
                module.use_uuid(uuid)
            actual_value = getattr(module, name)
            self.assertEquals(actual_value, expected_value,
                              "The value %s for module %s was not autoloaded by UUID" % (name, repr(module)))
            self.assertEquals(module.state, "loaded", "The module state was not 'loaded' after being autoloaded")

    @parameterized.expand(module_provider())
    def test_uuid(self, module_class):
        module_class.reset()
        module = module_class()
        with self.assertNumQueries(1):
            self.assertEquals(module.state, "found", "The module state must be flushed to FOUND after the module reset")
            self.assertIsInstance(module._uuid, str, "The module UUID must be erased after the module reset")
            self.assertIsInstance(module.uuid, UUID, "The module UUID must be an instance of UUID class")
            self.assertEquals(module.state, "loaded", "The module must be autoloaded when accessing to its UUID")
            with self.assertRaises(ValueError,
                                   msg="The corefacility module's uuid property is not read-only"):
                module.uuid = uuid4()

    @parameterized.expand(module_provider())
    def test_parent_entry_point(self, module_class):
        module_class.reset()
        module = module_class()
        with self.assertNumQueries(0):
            self.assertEquals(module.state, "found", "The module state must be flushed to FOUND after the module reset")
            parent_ep = module.parent_entry_point
            if isinstance(module, CoreApp):
                self.assertIsNone(parent_ep, "The core module must not be attached to any entry point")
            else:
                self.assertIsInstance(parent_ep, EntryPoint,
                                      "The module's parent entry point must be an instance of EntryPoint")
            self.assertEquals(module.state, "found", "The module's parent entry point property is not autoloading")
            with self.assertRaises(ValueError, msg="The module's parent entry point is read-only property"):
                module.parent_entry_point = AuthorizationsEntryPoint()

    @parameterized.expand(read_only_property_provider())
    def test_read_only_property(self, module_class, property_name, expected_class, test_value, can_be_none):
        module_class.reset()
        module = module_class()
        with self.assertNumQueries(0):
            self.assertEquals(module.state, "found", "The module state was not flushed during the module reset")
            property_value = getattr(module, property_name)
            if not can_be_none or property_value is not None:
                self.assertIsInstance(property_value, expected_class,
                                      "The property %s for the module is not an instance of %s" %
                                      (property_name, expected_class.__name__))
            self.assertEquals(module.state, "found",
                              "Accessing read-only default properties shall not change the module state")
            with self.assertRaises(ValueError, msg="The module property %s is not read-only" % property_name):
                setattr(module, property_name, test_value)

    @parameterized.expand(is_enabled_provider())
    def test_is_enabled(self, module_class, value):
        module_class.reset()
        module = module_class()
        with self.assertNumQueries(1):
            self.assertEquals(module.state, "found", "The module state was not flushed during the module reset")
            old_value = module.is_enabled
            self.assertEquals(module.state, "loaded", "The module was not autoloaded during the enability")
            self.assertIsInstance(old_value, bool, "The module is_enabled property is not boolean")
            module.is_enabled = value
            self.assertEquals(module.state, "changed", "The module state doesn't moved to 'changed'")
        module.update()
        self.assertEquals(module.state, "saved", "The module state doesn't moved to SAVED after property save")
        self.assertEquals(module.is_enabled, value, "The module is_enabled value doesn't stored correctly")
        del module
        module_class.reset()
        module = module_class()
        self.assertEquals(module.is_enabled, value, "The module is_enabled state can't be correctly transmitted")

    @parameterized.expand(user_settings_provider())
    def test_user_settings(self, module_class, sample_name, sample_value, default_value):
        module_class.reset()
        module = module_class()
        with self.assertNumQueries(1):
            self.assertEquals(module.state, "found", "The module state was not flushed during the module reset")
            actual_value = module.user_settings.get(sample_name, default_value)
            self.assertEquals(module.state, "loaded",
                              "The module was not autoloaded during the access to user settings")
            self.assertEquals(actual_value, default_value,
                              "The module setting shall be equal to its default value when it has not been setup")
            module.user_settings.set(sample_name, sample_value)
            self.assertEquals(module.state, "changed", "The module state doesn't moved to 'changed'")
        module.update()
        self.assertEquals(module.state, "saved", "The module state doesn't moved to SAVED after property save")
        self.assertEquals(module.user_settings.get(sample_name), sample_value,
                          "The module user settings was not stored perfectly")
        del module
        module_class.reset()
        module = module_class()
        self.assertEquals(module.user_settings.get(sample_name), sample_value,
                          "The module user settings was not transmitted correctly")
