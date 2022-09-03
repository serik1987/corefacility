from pathlib import Path
from rest_framework import status
from parameterized import parameterized

from core.test.data_providers.file_data_provider import file_data_provider
from imaging import App as ImagingApp
from imaging.entity import Map

from ..base_view_test import BaseViewTest
from ..project_data_test_mixin import ProjectDataTestMixin

MAP_CREATE_FILE = Path(__file__).parent / "test_cases/imaging_map_create.csv"
MAP_UPDATE_FILE = Path(__file__).parent / "test_cases/imaging_map_update.csv"
MAP_VIEW_FILE = Path(__file__).parent / "test_cases/imaging_map_view.csv"
MAP_DELETE_FILE = Path(__file__).parent / "test_cases/imaging_map_delete.csv"


class TestImagingPermissions(ProjectDataTestMixin, BaseViewTest):
    """
    Provides testing imaging permissions
    """

    ENTITY_APPLICATION_CLASS = ImagingApp
    IMAGING_LIST_PATH = "/api/{version}/core/projects/{project_alias}/imaging/data/"
    IMAGING_DETAIL_PATH = "/api/{version}/core/projects/{project_alias}/imaging/data/{data_alias}/"

    IMAGING_DATA = {
        "alias": "c023_X210",
        "type": "ori",
    }

    UPDATED_DATA = {"type": "dir"}

    @staticmethod
    def convert_arg_types(is_module_enabled, response_status):
        """
        Converts argument types from string to their proper types
        """
        if isinstance(is_module_enabled, str):
            is_module_enabled = True if is_module_enabled == "True" else False
        if isinstance(response_status, str):
            response_status = int(response_status)
        return is_module_enabled, response_status

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_project_data_environment()

    @parameterized.expand(file_data_provider(MAP_CREATE_FILE))
    def test_create_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
        """
        tests the entity create permissions
        """
        is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
        self.apply_args(is_module_enabled, project_alias, processors_mode)
        imaging_list_path = self.IMAGING_LIST_PATH.format(version=self.API_VERSION, project_alias=project_alias)
        headers = self.get_authorization_headers(token_id)
        response = self.client.post(imaging_list_path, self.IMAGING_DATA, format="json", **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected response status")

    @parameterized.expand(file_data_provider(MAP_UPDATE_FILE))
    def test_update_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
        """
        tests the entity update permissions
        """
        is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
        self.apply_args(is_module_enabled, project_alias, processors_mode)
        self.create_test_entity(project_alias)
        imaging_detail_path = self.IMAGING_DETAIL_PATH.format(
            version=self.API_VERSION, project_alias=project_alias, data_alias=self.IMAGING_DATA['alias'])
        headers = self.get_authorization_headers(token_id)
        response = self.client.patch(imaging_detail_path, self.UPDATED_DATA, format="json", **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected response status")

    @parameterized.expand(file_data_provider(MAP_VIEW_FILE))
    def test_get_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
        """
        Tests the entity reveal permissions
        """
        is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
        self.apply_args(is_module_enabled, project_alias, processors_mode)
        self.create_test_entity(project_alias)
        imaging_detail_path = self.IMAGING_DETAIL_PATH.format(
            version=self.API_VERSION, project_alias=project_alias, data_alias=self.IMAGING_DATA['alias']
        )
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(imaging_detail_path, **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected response status")

    @parameterized.expand(file_data_provider(MAP_DELETE_FILE))
    def test_destroy_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
        """
        Tests the entity destruction
        """
        is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
        self.apply_args(is_module_enabled, project_alias, processors_mode)
        self.create_test_entity(project_alias)
        imaging_detail_path = self.IMAGING_DETAIL_PATH.format(
            version=self.API_VERSION, project_alias=project_alias, data_alias=self.IMAGING_DATA['alias']
        )
        headers = self.get_authorization_headers(token_id)
        response = self.client.delete(imaging_detail_path, **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected response status")

    def apply_args(self, is_module_enabled, project_alias, processors_mode):
        """
        Changes application enability and project-application link enability depending on the input arguments
        """
        app = self.ENTITY_APPLICATION_CLASS()
        app.is_enabled = is_module_enabled
        app.update()
        self.change_modules_enability(project_alias, processors_mode)

    def create_test_entity(self, project_alias):
        project = self._project_set_object.get_by_alias(project_alias)
        functional_map = Map(**self.IMAGING_DATA)
        functional_map.project = project
        functional_map.create()
