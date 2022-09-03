from pathlib import Path

from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from core.test.data_providers.file_data_provider import file_data_provider

from imaging import App as ImagingApp
from imaging.entity import Map
from roi import App as RoiApp

from .base_test_class import BaseTestClass
from ..project_data_test_mixin import ProjectDataTestMixin

IMAGING_TEST_CASE_LIST_FILE = Path(__file__).parent.parent / "permissions_test/test_cases/ep_imaging.csv"
PROCESSORS_TEST_CASE_LIST_FILE = Path(__file__).parent.parent / "permissions_test/test_cases/ep_processors.csv"


class TestApplicationList(ProjectDataTestMixin, BaseTestClass):
    """
    Provides security tests for the ApplicationListView
    """

    PROJECT_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/"
    PROCESSORS_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/imaging/processors/{data_lookup}/"
    SETTINGS_APPLICATION_LIST_PATH = "/api/{version}/settings/"

    functional_maps = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_project_data_environment()
        cls.functional_maps = dict()
        for project in cls._project_set_object:
            functional_map = Map(alias="%s_map" % project.alias, type="ori", project=project)
            functional_map.create()
            cls.functional_maps[project.alias] = functional_map

    @parameterized.expand(file_data_provider(IMAGING_TEST_CASE_LIST_FILE))
    def test_projects_list(self, login, project, processors_mode, expected_status_code, module_count):
        """
        Tests user's module list for the imaging entry point
        :param login: particular user's login
        :param project: project which application list should be revealed
        :param processors_mode: 'none' to remain all application processors intact, 'all_enabled' to enable all
            application processors, 'all_disabled' to disable all application processors
        :param expected_status_code: status code to be expected
        :param module_count: number of modules in the list
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

    @parameterized.expand(file_data_provider(PROCESSORS_TEST_CASE_LIST_FILE))
    def test_processors_list(self, login, project, processors_mode, expected_status_code, module_count):
        """
        Tests user's module list for the processors entry point
        :param login: particular user's login
        :param project: project which application list should be revealed
        :param processors_mode: 'none' to remain all application processors intact, 'all_enabled' to enable all
            application processors, 'all_disabled' to disable all application processors
        :param expected_status_code: status code to be expected
        :param module_count: number of modules in the list
        """
        expected_status_code, module_count = int(expected_status_code), int(module_count)
        self.change_modules_enability(project, processors_mode)
        functional_map = self.functional_maps[project]
        request_path = self.PROCESSORS_APPLICATION_LIST_PATH.format(
            version=self.API_VERSION,
            project_lookup=project,
            data_lookup=functional_map.alias
        )
        response_data = self.make_test_request(login, request_path, expected_status_code)
        if expected_status_code == status.HTTP_200_OK:
            self.assert_map_detail(response_data['map_info'], self.functional_maps[project])
            self.assertEquals(len(response_data['module_list']), module_count, "Unexpected number of modules")
            if module_count == 1:
                self.assert_module_detail(response_data['module_list'][0], RoiApp())

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

    def assert_map_detail(self, actual_info, expected_info):
        """
        Asserts that two functional maps are the same to each other
        :param actual_info: map info that has been sent to the client
        :param expected_info: map info that has been stored in the database
        :return: nothing
        """
        self.assertEquals(actual_info['id'], expected_info.id, "Map IDs are not the same")
        self.assertEquals(actual_info['alias'], expected_info.alias, "Map aliases are not the same")
        self.assertEquals(actual_info['type'], str(expected_info.type), "Map types are not the same")

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
