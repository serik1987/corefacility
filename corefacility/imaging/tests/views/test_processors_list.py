from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from core.test.views.base_view_test import BaseViewTest
from roi import App as RoiApp

from .map_list_mixin import MapListMixin


class TestProcessorsList(MapListMixin, BaseViewTest):
    """
    Tests the processors list
    """

    PROCESSORS_LIST_PATH = "/api/{version}/core/projects/{project_name}/imaging/processors/{map_name}/"

    roi_definition_name = None

    functional_map = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_environment(add_roi_application=True)
        cls.roi_definition_name = gettext(RoiApp().name)

    def setUp(self):
        super().setUp()
        self.initialize_projects()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_test_environment()
        super().tearDownClass()

    @parameterized.expand([
        ("full", 1, 3, status.HTTP_404_NOT_FOUND),
        ("data_full", 0, 0, status.HTTP_200_OK),
        ("data_view", 0, 2, status.HTTP_200_OK),
        ("full", 0, 4, status.HTTP_404_NOT_FOUND),
        ("full", 1, 2, status.HTTP_404_NOT_FOUND),
        ("data_process", 1, 4, status.HTTP_200_OK),
        ("data_process", 0, 2, status.HTTP_200_OK),
        ("no_access", 0, 0, status.HTTP_404_NOT_FOUND),
        ("no_access", 1, 5, status.HTTP_404_NOT_FOUND),
        ("superuser", 1, 1, status.HTTP_404_NOT_FOUND),
        ("data_full", 0, 3, status.HTTP_200_OK),
        ("no_access", 1, 0, status.HTTP_404_NOT_FOUND),
        ("data_view", 1, 1, status.HTTP_404_NOT_FOUND),
        ("data_full", 0, 4, status.HTTP_404_NOT_FOUND),
        ("data_process", 1, 3, status.HTTP_404_NOT_FOUND),
        ("no_access", 0, 1, status.HTTP_404_NOT_FOUND),
        ("data_process", 0, 1, status.HTTP_200_OK),
        ("data_view", 1, 4, status.HTTP_200_OK),
        ("data_view", 1, 3, status.HTTP_404_NOT_FOUND),
        ("superuser", 1, 0, status.HTTP_404_NOT_FOUND),
        ("no_access", 0, 3, status.HTTP_404_NOT_FOUND),
        ("full", 0, 1, status.HTTP_200_OK),
        ("data_full", 1, 1, status.HTTP_404_NOT_FOUND),
        ("no_access", 0, 4, status.HTTP_404_NOT_FOUND),
        ("superuser", 1, 5, status.HTTP_200_OK),
        ("data_full", 0, 5, status.HTTP_404_NOT_FOUND),
        ("data_view", 1, 0, status.HTTP_404_NOT_FOUND),
        ("full", 0, 0, status.HTTP_200_OK),
        ("full", 1, 5, status.HTTP_200_OK),
        ("data_process", 1, 5, status.HTTP_200_OK),
        ("superuser", 1, 4, status.HTTP_200_OK),
        ("data_process", 1, 2, status.HTTP_404_NOT_FOUND),
    ])
    def test_processors_list_sample(self, token_id, project_index, map_index, expected_status_code):
        """
        Provides simple test of the processor list (with assertions)
        :param token_id: request sender's login
        :param project_index: 0 for 'test_project', 1 for 'test_project1'
        :param map_index: index of the map within the test environment
        :param expected_status_code: status code to be expected
        :return: nothing
        """
        detail_path = self.get_list_path(project_index, map_index)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(detail_path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")
        if expected_status_code <= status.HTTP_300_MULTIPLE_CHOICES:
            self.assert_module_list(response.data['module_list'])
            self.assert_map_info(response.data['map_info'], self.functional_map)

    def assert_module_list(self, module_list):
        self.assertEquals(len(module_list), 1, "Unexpected module count")
        actual_module = module_list[0]
        expected_module = RoiApp()
        self.assertEquals(actual_module['alias'], expected_module.alias, "Unexpected ROI module alias")
        self.assertEquals(actual_module['name'], self.roi_definition_name, "Unexpected ROI module name")
        self.assertEquals(actual_module['uuid'], str(expected_module.uuid), "Unexpected ROI module UUID")

    def assert_map_info(self, actual_map, expected_map):
        self.assertEquals(actual_map['id'], expected_map.id, "Unexpected map ID")
        self.assertEquals(actual_map['alias'], expected_map.alias, "Unexpected map alias")
        self.assertEquals(actual_map['type'], str(expected_map.type), "Unexpected map type")

    def get_list_path(self, project_index, map_index):
        """
        Estimates the processors list path
        :param project_index: index of the project within the project list
        :param map_index: index of the map within the functional map list
        :return: nothing
        """
        project_alias = self.projects[project_index].alias
        first_project_map_number = len(self.project_maps['test_project'])
        if map_index < first_project_map_number:
            functional_map = self.project_maps['test_project'][map_index]
        else:
            functional_map = self.project_maps['test_project1'][map_index - first_project_map_number]
        self.functional_map = functional_map
        return self.PROCESSORS_LIST_PATH.format(
            version=self.API_VERSION, project_name=project_alias,
            map_name=functional_map.alias,
        )
