from pathlib import Path

from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from core.models.enums import LevelType
from core.entity.access_level import AccessLevelSet
from core.entity.entry_points.authorizations import AuthorizationModule
from core.test.data_providers.file_data_provider import file_data_provider
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject
from core.test.entity_set.entity_set_objects.project_application_set_object import ProjectApplicationSetObject

from imaging import App as ImagingApp

from .base_test_class import BaseTestClass

TEST_CASE_LIST_FILE = Path(__file__).parent.parent / "permissions_test/test_cases/processors.csv"


class TestApplicationList(BaseTestClass):
    """
    Provides security tests for the ApplicationListView
    """

    PROJECT_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/"
    PROCESSORS_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/imaging/processors/{data_lookup}/"
    SETTINGS_APPLICATION_LIST_PATH = "/api/{version}/settings/"

    _access_levels = None
    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _project_application_set_object = None

    superuser_required = True
    ordinary_user_required = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._load_access_levels()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object.clone())
        cls._project_set_object = ProjectSetObject(cls._group_set_object.clone())
        cls._project_application_set_object = ProjectApplicationSetObject(cls._project_set_object.clone())
        cls.issue_tokens()

    @classmethod
    def _load_access_levels(cls):
        level_set = AccessLevelSet()
        level_set.type = LevelType.app_level
        cls._access_levels = {}
        for level in level_set:
            cls._access_levels[level.alias] = level

    @classmethod
    def issue_tokens(cls):
        for user in cls._user_set_object:
            token = AuthorizationModule.issue_token(user)
            setattr(cls, "%s_token" % user.login, token)

    @parameterized.expand(file_data_provider(TEST_CASE_LIST_FILE))
    def test_projects_list(self, login="user1", project="hhna", processors_mode="none",
                           expected_status_code=status.HTTP_200_OK, module_count=1):
        """
        Tests whether application list related to a single project is correctly resolved
        :param login: particular user's login
        :param project: project which application list should be revealed
        :param processors_mode: 'none' to remain all application processors intact, 'all_enabled' to enable all
            application processors, 'all_disabled' to disable all application processors
        :param expected_status_code: status code to be expected
        :param module_count: number of modules in the list
        :return:
        """
        self.change_modules_enability(project, processors_mode)
        module_list_path = self.PROJECT_APPLICATION_LIST_PATH.format(
            version=self.API_VERSION,
            project_lookup=project
        )
        response_data = self.make_test_request(login, module_list_path, expected_status_code)
        if expected_status_code == status.HTTP_200_OK:
            self.assert_project_detail(response_data['project_info'], self._project_set_object.get_by_alias(project))
            self.assertEquals(len(response_data['module_list']), module_count, "Unexpected number of modules")
            if module_count == 1:
                self.assert_module_detail(response_data['module_list'][0], ImagingApp())

    def change_modules_enability(self, project_alias, processors_mode):
        """
        Makes all modules either enabled or disabled
        :param project_alias: project's alias
        :param processors_mode: 'all_enabled', 'all_disabled' or 'none' depending on the action
        :return: nothing
        """
        for project_application_record in self._project_application_set_object:
            if project_application_record.project.alias == project_alias:
                if processors_mode == "all_enabled":
                    project_application_record.is_enabled = True
                    project_application_record.update()
                if processors_mode == "all_disabled":
                    project_application_record.is_enabled = False
                    project_application_record.update()

    def make_test_request(self, login, module_list_path, expected_status_code):
        """
        Makes the test request that returns list of all modules
        :param login: user's login
        :param module_list_path: the request path
        :param expected_status_code: expecting response status code
        :return: the response data
        """
        request_headers = self.get_authorization_headers(login) if login != "not-authorized" else {}
        response = self.client.get(module_list_path, **request_headers)
        if isinstance(expected_status_code, str):
            expected_status_code = int(expected_status_code)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")
        return response.data

    def assert_project_detail(self, actual_info, expected_info):
        """
        Asserts that the project details correspond to given ones
        :param actual_info: actual project details
        :param expected_info: expected project details
        """
        self.assertEquals(actual_info['id'], expected_info.id, "Project IDs are not the same")
        self.assertEquals(actual_info['alias'], expected_info.alias, "Project aliases are not the same")
        self.assertEquals(actual_info['name'], expected_info.name, "Project names are not the same")
        self.assertEquals(actual_info['root_group']['id'], expected_info.root_group.id,
                          "Project root groups are not the same")
        self.assertEquals(actual_info['root_group']['name'], expected_info.root_group.name,
                          "Root group names are not the same")
        self.assertEquals(actual_info['governor']['id'], expected_info.governor.id,
                          "Project governors are not the same")
        self.assertEquals(actual_info['governor']['login'], expected_info.governor.login,
                          "Governor logins are not the same")
        self.assertEquals(actual_info['governor']['name'], expected_info.governor.name,
                          "Governor names are not the same")
        self.assertEquals(actual_info['governor']['surname'], expected_info.governor.surname,
                          "Governor surnames are not the same")

    def assert_module_detail(self, actual_info, expected_info):
        """
        Asserts that the module details are the same to each other
        :param actual_info: actual module info
        :param expected_info: expected module info
        """
        self.assertEquals(actual_info['uuid'], str(expected_info.uuid), "Module UUIDs are not the same")
        self.assertEquals(actual_info['alias'], expected_info.alias, "Unexpected module alias")
        self.assertEquals(actual_info['name'], gettext(expected_info.name), "Unexpected module name")


del BaseTestClass
