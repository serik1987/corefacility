from parameterized import parameterized

from imaging import App as ImagingApp
from roi import App as RoiApp

from core.test.data_providers.entity_sets import filter_data_provider
from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.project_application_set_object import ProjectApplicationSetObject


def base_search_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 11, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 11, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 12, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (3, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (-1, 7, 1), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (0, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (6, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (7, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, None, None), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, None, None), BaseTestClass.POSITIVE_TEST_CASE),
    ]


def is_enabled_search_provider():
    return filter_data_provider(
        (True, False),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    )


def project_search_provider():
    return filter_data_provider(
        (0, 3, 6),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    )


def application_search_provider():
    return filter_data_provider(
        (ImagingApp(), RoiApp()),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    )


class TestProjectApplicationSet(BaseTestClass):
    """
    Tests the ProjectApplicationSet entity set
    """

    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _project_application_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object.clone())
        cls._project_set_object = ProjectSetObject(cls._group_set_object.clone())
        cls._project_application_set_object = ProjectApplicationSetObject(cls._project_set_object.clone())

    def setUp(self):
        self._container = self._project_application_set_object.clone()
        self.initialize_filters()

    @parameterized.expand(base_search_provider())
    def test_base_search(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(is_enabled_search_provider())
    def test_entity_is_enabled_search(self, is_enabled, *args):
        self.apply_filter("entity_is_enabled", is_enabled)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(project_search_provider())
    def test_project_search(self, project_index, *args):
        project = self._project_set_object[project_index]
        self.apply_filter("project", project)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(application_search_provider())
    def test_application_search(self, app, *args):
        self.apply_filter("application", app)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(is_enabled_search_provider())
    def test_application_is_enabled(self, is_enabled, *args):
        self.apply_filter("application_is_enabled", is_enabled)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        """
        Asserts that the entity has been successfully found.
        Class derivatives can re-implement this method to ensure that all entity fields were uploaded successfully.

        :param actual_entity: the entity found in the database
        :param expected_entity: the entity expected to be found in the database
        :param msg: message to print when the entity is failed to be found
        :return: nothing
        """
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.is_enabled, expected_entity.is_enabled,
                          msg + ". The is_enabled property was not retrieved correctly")
        self.assertEquals(actual_entity.application, expected_entity.application,
                          msg + ". The application property was not retrieved correctly")
        self.assertEquals(actual_entity.project, expected_entity.project,
                          msg + ". The project property was not retrieved correctly")
        self.assertEquals(actual_entity.project.root_group, expected_entity.project.root_group,
                          msg + ". The project root group was not retrieved correctly")
        self.assertEquals(actual_entity.project.governor, expected_entity.project.governor,
                          msg + ". The project governor was not retrieved correctly")


del BaseTestClass
