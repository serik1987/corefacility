from parameterized import parameterized

from ...data_providers.file_data_provider import file_data_provider

from ..base_view_test import BaseViewTest
from ..project_data_test_mixin import ProjectDataTestMixin


def generate_test_class(
        arg_entity_create_file=None,
        arg_entity_update_file=None,
        arg_entity_get_file=None,
        arg_entity_destroy_file=None,
        arg_include_create_test=True,
        arg_include_update_test=True,
        arg_include_get_test=True,
        arg_include_destroy_test=True
):

    class TestApplicationPermission(ProjectDataTestMixin, BaseViewTest):
        """
        Provides testing imaging permissions
        """

        ENTITY_APPLICATION_CLASS = None
        ENTITY_LIST_PATH = None
        ENTITY_DETAIL_PATH = None
        SOURCE_DATA = None
        UPDATED_DATA = None

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

        if arg_include_create_test:
            @parameterized.expand(file_data_provider(arg_entity_create_file))
            def test_create_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
                """
                tests the entity create permissions
                """
                is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
                self.apply_args(is_module_enabled, project_alias, processors_mode)
                entity_list_path = self.ENTITY_LIST_PATH.format(version=self.API_VERSION, project_alias=project_alias)
                headers = self.get_authorization_headers(token_id)
                response = self.client.post(entity_list_path, self.SOURCE_DATA, format="json", **headers)
                self.assertEquals(response.status_code, response_status, "Unexpected response status")

        if arg_include_update_test:
            @parameterized.expand(file_data_provider(arg_entity_update_file))
            def test_update_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
                """
                tests the entity update permissions
                """
                is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
                self.apply_args(is_module_enabled, project_alias, processors_mode)
                entity_id = self.create_test_entity(project_alias)
                entity_detail_path = self.ENTITY_DETAIL_PATH.format(
                    version=self.API_VERSION, project_alias=project_alias, data_alias=entity_id)
                headers = self.get_authorization_headers(token_id)
                response = self.client.patch(entity_detail_path, self.UPDATED_DATA, format="json", **headers)
                self.assertEquals(response.status_code, response_status, "Unexpected response status")

        if arg_include_get_test:
            @parameterized.expand(file_data_provider(arg_entity_get_file))
            def test_get_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
                """
                Tests the entity reveal permissions
                """
                is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
                self.apply_args(is_module_enabled, project_alias, processors_mode)
                entity_id = self.create_test_entity(project_alias)
                entity_detail_path = self.ENTITY_DETAIL_PATH.format(
                    version=self.API_VERSION, project_alias=project_alias, data_alias=entity_id
                )
                headers = self.get_authorization_headers(token_id)
                response = self.client.get(entity_detail_path, **headers)
                self.assertEquals(response.status_code, response_status, "Unexpected response status")

        if arg_include_destroy_test:
            @parameterized.expand(file_data_provider(arg_entity_destroy_file))
            def test_destroy_entity(self, is_module_enabled, token_id, project_alias, processors_mode, response_status):
                """
                Tests the entity destruction
                """
                is_module_enabled, response_status = self.convert_arg_types(is_module_enabled, response_status)
                self.apply_args(is_module_enabled, project_alias, processors_mode)
                entity_id = self.create_test_entity(project_alias)
                entity_detail_path = self.ENTITY_DETAIL_PATH.format(
                    version=self.API_VERSION, project_alias=project_alias, data_alias=entity_id
                )
                headers = self.get_authorization_headers(token_id)
                response = self.client.delete(entity_detail_path, **headers)
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
            """
            We need to create tested entity for PUT/PATCH, GET and DELETE requests
            :param project_alias: alias of the project where test entity shall be created
            :return: ID for the created entity
            """
            raise NotImplementedError("create_test_entity")

    return TestApplicationPermission
