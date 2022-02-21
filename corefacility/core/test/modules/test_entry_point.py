from django.utils.module_loading import import_string
from parameterized import parameterized

from core import App as CoreApp, AuthorizationsEntryPoint, SettingsEntryPoint, SynchronizationsEntryPoint, \
    ProjectsEntryPoint
from core.entity.entry_points.entry_point_set import EntryPointSet
from core.entity.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException
from imaging import App as ImagingApp, ProcessorsEntryPoint

from core.test.data_providers.module_providers import entry_point_provider
from core.test.data_providers.entity_sets import filter_data_provider
from core.test.entity.base_apps_test import BaseAppsTest
from core.test.entity.entity_objects.entry_point_set_object import EntryPointSetObject


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


def core_entry_points_provider():
    return [
        (AuthorizationsEntryPoint,),
        (SettingsEntryPoint,),
        (SynchronizationsEntryPoint,),
        (ProjectsEntryPoint,),
    ]


def core_entry_point_with_parent_module_provider():
    return [
        (AuthorizationsEntryPoint, CoreApp()),
        (SettingsEntryPoint, CoreApp()),
        (SynchronizationsEntryPoint, CoreApp()),
        (ProjectsEntryPoint, CoreApp()),
        (ProcessorsEntryPoint, ImagingApp())
    ]


def entry_point_alias_provider():
    return [
        (AuthorizationsEntryPoint, "authorizations"),
        (SettingsEntryPoint, "settings"),
        (SynchronizationsEntryPoint, "synchronizations"),
        (ProjectsEntryPoint, "projects"),
        (ProcessorsEntryPoint, "processors"),
    ]


def entry_point_name_provider():
    return [
        (AuthorizationsEntryPoint, "Authorization methods"),
        (SettingsEntryPoint, "Other settings"),
        (SynchronizationsEntryPoint, "Account synchronization"),
        (ProjectsEntryPoint, "Project applications"),
        (ProcessorsEntryPoint, "Imaging processors"),
    ]


def entry_point_type_provider():
    return [
        (AuthorizationsEntryPoint, "lst"),
        (SettingsEntryPoint, "lst"),
        (SynchronizationsEntryPoint, "sel"),
        (ProjectsEntryPoint, "lst"),
        (ProcessorsEntryPoint, "lst"),
    ]


def entry_point_class_provider():
    return [
        (entry_point, "%s.%s" % (entry_point.__module__, entry_point.__name__))
        for entry_point in (
            AuthorizationsEntryPoint,
            SettingsEntryPoint,
            SynchronizationsEntryPoint,
            ProjectsEntryPoint,
            ProcessorsEntryPoint
        )
    ]


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

    @parameterized.expand(entry_point_classes_provider())
    def test_find_entry_point_by_id(self, entry_point_class):
        entry_point_id = entry_point_class().id
        entry_point_set = EntryPointSet()
        with self.assertLessQueries(1):
            entry_point = entry_point_set.get(entry_point_id)
            self.assertIsInstance(entry_point, entry_point_class,
                                  "The incorrect entry point was found")

    @parameterized.expand(entry_point_classes_provider())
    def test_find_entry_point_by_alias_positive(self, entry_point_class):
        old_entry_point = entry_point_class()
        belonging_module = old_entry_point.belonging_module
        alias = old_entry_point.alias
        del old_entry_point
        entry_point_set = EntryPointSet()
        entry_point_set.parent_module = belonging_module
        with self.assertLessQueries(1):
            entry_point = entry_point_set.get(alias)
            self.assertIsInstance(entry_point, entry_point_class, "The incorrect entry point was found")

    @parameterized.expand(core_entry_points_provider())
    def test_find_entry_point_by_alias_root(self, entry_point_class):
        alias = entry_point_class().alias
        with self.assertLessQueries(1):
            entry_point_set = EntryPointSet()
            entry_point_set.parent_module_is_root = True
            entry_point = entry_point_set.get(alias)
            self.assertIsInstance(entry_point, entry_point_class, "The incorrect entry point was found")

    @parameterized.expand(entry_point_classes_provider())
    def test_find_entry_point_by_alias_negative(self, entry_point_class):
        old_entry_point = entry_point_class()
        alias = old_entry_point.alias
        del old_entry_point
        entry_point_set = EntryPointSet()
        with self.assertLessQueries(1):
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="Application of get(alias) method without parent_module being specified"
                                       "must always raise an exception because such operation is ambiguous"):
                entry_point_set.get(alias)

    @parameterized.expand(entry_point_classes_provider())
    def test_reset(self, entry_point_class):
        entry_point_class.reset()
        with self.assertNumQueries(0):
            entry_point = entry_point_class()
            self.assertEquals(entry_point.state, "found", "The entry point state is not FOUND")
            self.assertEntryPointFound(entry_point)
            self.assertIsNone(entry_point._belonging_module,
                              "The belonging module shall not be loaded automatically during the startup")

    @parameterized.expand(core_entry_point_with_parent_module_provider())
    def test_autoload(self, entry_point_class, parent_module):
        entry_point_class.reset()
        parent_module = parent_module.__class__()
        with self.assertNumQueries(1):
            entry_point = entry_point_class()
            self.assertIsInstance(entry_point.id, int, "The entry point ID must be integer after the autoload")
            self.assertEquals(entry_point.belonging_module.uuid, parent_module.uuid,
                              "The belonging module for the entry point is not the same as expected")
            self.assertEquals(entry_point.state, "loaded", "The entry point doesn't switch its state to 'loaded'")

    def test_delete_settings_entry_point(self):
        entry_point = SettingsEntryPoint()
        entry_point_id = entry_point.id
        entry_point.delete()
        self.assertEquals(entry_point.state, "deleted", "The entry point state must be DELETED after its delete")
        self.assertEquals(entry_point.id, None, "The entry point ID property must be readable")
        self.assertEquals(entry_point.belonging_module, None,
                          "The belonging module must be detached after entry point destruction")
        self.assertEntryPointFound(entry_point)
        entry_point_set = EntryPointSet()
        with self.assertRaises(EntityNotFoundException,
                               msg="The entity can be found in the database even though after its delete"):
            entry_point_set.get(entry_point_id)
        SettingsEntryPoint.reset()
        entry_point = SettingsEntryPoint()
        self.assertEquals(entry_point.state, "found",
                          "When entry point was deleted and resetted its state must be found")
        self.assertEquals(entry_point.id, None,
                          "The entry point ID must be 'uninstalled' when the entry point has been found")
        self.assertEquals(entry_point.belonging_module, None,
                          "The entry point must be de-attached from the root module even after its reload "
                          "after uninstall")
        self.assertEntryPointFound(entry_point)

    @parameterized.expand(core_entry_point_with_parent_module_provider())
    def test_belonging_module(self, entry_point_class, expected_value):
        expected_value = expected_value.__class__()
        self._test_entry_point_field(entry_point_class, "belonging_module", expected_value)

    @parameterized.expand(entry_point_alias_provider())
    def test_alias(self, entry_point_class, expected_value):
        self._test_entry_point_field(entry_point_class, "alias", expected_value)

    @parameterized.expand(entry_point_name_provider())
    def test_name(self, entry_point_class, expected_value):
        self._test_entry_point_field(entry_point_class, "name", expected_value)

    @parameterized.expand(entry_point_type_provider())
    def test_type(self, entry_point_class, expected_value):
        self._test_entry_point_field(entry_point_class, "type", expected_value)

    @parameterized.expand(entry_point_class_provider())
    def test_entry_point_class(self, entry_point_class, expected_value):
        self._test_entry_point_field(entry_point_class, "entry_point_class", expected_value)

    def _test_entry_point_field(self, entry_point_class, name, expected_value):
        entry_point = entry_point_class()
        actual_value = getattr(entry_point, name)
        self.assertEquals(actual_value, expected_value, "Invalid value for the property '%s' of %s"
                          % (name, repr(entry_point)))
        with self.assertRaises(ValueError, msg="All entry point fields must be read only"):
            setattr(entry_point, name, expected_value)

    def assertEntryPointFound(self, entry_point):
        self.assertEquals(entry_point.alias, entry_point.get_alias(),
                          "The entry point alias is not the same as stated by the developer")
        self.assertEquals(entry_point.name, entry_point.get_name(),
                          "The entry point name is not the same as stated by the developer")
        self.assertEquals(entry_point.type, entry_point.get_type(),
                          "The entry point type is not the same as stated by the developer")
        actual_entry_point_class = import_string(entry_point.entry_point_class)
        self.assertIs(actual_entry_point_class, entry_point.__class__,
                      "The entry point has an invalid value of the 'entry_point_class' property")
