from parameterized import parameterized

from ..entity_set.base_test_class import BaseTestClass
from ..entity_set.entity_set_objects.user_set_object import UserSetObject
from ..entity_set.entity_set_objects.group_set_object import GroupSetObject
from ..entity_set.entity_set_objects.project_set_object import ProjectSetObject
from ..entity.entity_objects.corefacility_module_set_object import CorefacilityModuleSetObject
from ..data_providers.entity_sets import filter_data_provider


def project_provider():
    return filter_data_provider(
        range(10),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    )


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

    def setUp(self):
        self._container = self._corefacility_module_set_object.clone()

    @parameterized.expand(project_provider())
    def test_project_search(self, project_index, *args):
        project = self._project_set_object[project_index]
        self.apply_filter("project", project)
        self._test_all_access_features(*args)

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


del BaseTestClass
