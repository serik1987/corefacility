from pathlib import Path

from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from core.test.data_providers.file_data_provider import file_data_provider

from imaging import App as ImagingApp

from .base_test_class import BaseTestClass
from ..project_data_test_mixin import ProjectDataTestMixin

TEST_CASE_LIST_FILE = Path(__file__).parent.parent / "permissions_test/test_cases/ep_imaging.csv"


class TestApplicationList(ProjectDataTestMixin, BaseTestClass):
    """
    Provides security tests for the ApplicationListView
    """

    PROJECT_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/"
    PROCESSORS_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/imaging/processors/{data_lookup}/"
    SETTINGS_APPLICATION_LIST_PATH = "/api/{version}/settings/"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_project_data_environment()

    @parameterized.expand(file_data_provider(TEST_CASE_LIST_FILE))
    def test_projects_list(self, login, project, processors_mode, expected_status_code, module_count):
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
