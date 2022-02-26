from parameterized import parameterized

from core.entity.entity_sets.project_set import ProjectSet
from core.entity.entity_exceptions import EntityNotFoundException
from imaging import App as ImagingApp
from roi import App as RoiApp

from core.test.entity_set.base_test_class import BaseTestClass
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject
from core.test.entity.entity_objects.corefacility_module_set_object import CorefacilityModuleSetObject
from core.test.entity_set.entity_set_objects.project_application_set_object import ProjectApplicationSetObject
from core.test.data_providers.entity_sets import filter_data_provider


def project_provider():
    return filter_data_provider(
        range(10),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    )


def project_apps_get_provider():
    return [
        (0, "imaging", None),
        (0, "roi", None),
        (1, "imaging", None),
        (1, "roi", RoiApp()),
        (2, "roi", None),
        (2, "imaging", ImagingApp()),
        (3, "roi", None),
        (3, "imaging", None),
        (4, "imaging", None),
        (4, "roi", RoiApp()),
        (5, "imaging", None),
        (5, "roi", None),
        (6, "imaging", ImagingApp()),
        (6, "roi", None),
        (7, "roi", RoiApp()),
        (7, "imaging", None),
        (8, "roi", RoiApp()),
        (8, "imaging", None),
        (9, "imaging", None),
        (9, "roi", None),
    ]


def project_apps_len_provider():
    return [
        (0, 0), (1, 1), (2, 1), (3, 0), (4, 1), (5, 0), (6, 1), (7, 1), (8, 1), (9, 0)
    ]


class TestProjectFilter(BaseTestClass):
    """
    This is a special class to test the module's project filters
    """

    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _corefacility_module_set_object = None
    _project_application_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object.clone())
        cls._project_set_object = ProjectSetObject(cls._group_set_object.clone())
        cls._corefacility_module_set_object = CorefacilityModuleSetObject()
        cls._project_application_set_object = ProjectApplicationSetObject(cls._project_set_object.clone())

    def setUp(self):
        self._container = self._corefacility_module_set_object.clone()

    @parameterized.expand(project_provider())
    def test_project_search(self, project_index, *args):
        project = self._project_set_object[project_index]
        self.apply_filter("project", project)
        self._test_all_access_features(*args)

    @parameterized.expand(project_apps_get_provider())
    def test_project_apps_get(self, project_index, project_alias, expected_app):
        project = self._project_set_object[project_index]
        if expected_app is not None:
            actual_app = project.project_apps.get(project_alias)
            self.assertEquals(actual_app.uuid, expected_app.uuid,
                              "The project_app property must find a correct application by alias")
        else:
            with self.assertRaises(EntityNotFoundException, msg="This entity shall not be found"):
                project.project_apps.get(project_alias)

    @parameterized.expand(project_apps_len_provider())
    def test_project_apps_iter(self, project_index, expected_length):
        project = self._project_set_object[project_index]
        actual_length = 0
        for actual_app in project.project_apps:
            app_alias = actual_app.alias
            expected_app = project.project_apps.get(app_alias)
            self.assertIs(actual_app, expected_app, "Apps are not the same")
            actual_length += 1
        self.assertEquals(actual_length, expected_length, "Total number of iterated applications must be the same "
                                                          "as the result of len() function")

    @parameterized.expand(project_apps_len_provider())
    def test_project_apps_len(self, project_index, expected_length):
        project = self._project_set_object[project_index]
        actual_length = len(project.project_apps)
        self.assertEquals(actual_length, expected_length, "Total number of project applications is not the same "
                                                          "as expected")

    @parameterized.expand([
        (ImagingApp(),),
        (RoiApp(),),
    ])
    def test_filter_application(self, app):
        project_set = ProjectSet()
        project_set.application = app
        for project in project_set:
            expected_app = project.project_apps.get(app.alias)
            self.assertIs(app, expected_app, "The application filter remains projects that are not a part "
                                             "of the op")


del BaseTestClass
