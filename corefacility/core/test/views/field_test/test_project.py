from rest_framework import status
from parameterized import parameterized

from .base_test_class import BaseTestClass
from .data_providers import slug_provider, arbitrary_string_provider


class TestProject(BaseTestClass):
    """
    Provides field validation tests for single projects
    """

    resource_name = "projects"

    no_alias_data = {
        "name": "Some project",
        "root_group_id": None,
        "root_group_name": "Some project group"
    }

    no_name_data = {
        "alias": "some-project",
        "root_group_id": None,
        "root_group_name": "Some project group",
    }

    new_root_group_data = {
        "alias": "vasomotor-oscillations",
        "name": "Вазомоторные колебания",
        "root_group_id": None,
        "root_group_name": "Вазомоторные колебания",
    }

    @parameterized.expand(slug_provider(64))
    def test_alias_valid(self, alias_value, is_valid):
        """
        Checks the project alias validation feature

        :param alias_value: tested value
        :param is_valid: True is such an alias is valid, False otherwise
        :return: nothing
        """
        self._test_field_value("alias", "no_alias", alias_value, is_valid, True, alias_value)

    def test_alias_required(self):
        """
        Checks whether the alias field is treated as required

        :return: nothing
        """
        self._test_field_required("alias", "no_alias", True, True, None)

    def test_alias_duplicated(self):
        """
        Checks whether the client can create two projects with the same alias

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        path = self.get_entity_list_path()
        first_project_response = self.client.post(path, data=self.new_root_group_data, format="json", **headers)
        self.assertEquals(first_project_response.status_code, status.HTTP_201_CREATED,
                          "The first project creation must be successful")
        another_data = self.no_alias_data.copy()
        another_data['alias'] = self.new_root_group_data['alias']
        second_project_response = self.client.post(path, data=another_data, format="json", **headers)
        self.check_response_duplication_error(second_project_response)

    def test_alias_duplicated_change(self):
        """
        Checks whether the alias can be changed to the duplicated value

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        path = self.get_entity_list_path()
        first_project_create_response = self.client.post(path, data=self.new_root_group_data, format="json", **headers)
        self.assertEquals(first_project_create_response.status_code, status.HTTP_201_CREATED,
                          "The first project creation must be successful during this test")
        another_data = self.no_alias_data.copy()
        another_data['alias'] = 'another-alias'
        second_project_create_response = self.client.post(path, data=another_data, format="json", **headers)
        self.assertEquals(second_project_create_response.status_code, status.HTTP_201_CREATED)
        alias_modification_path = self.get_entity_detail_path(second_project_create_response.data['id'])
        alias_modification_response = self.client.patch(alias_modification_path,
                                                        data={"alias": "vasomotor-oscillations"},
                                                        format="json",
                                                        **headers)
        self.check_response_duplication_error(alias_modification_response)

    @parameterized.expand(arbitrary_string_provider(False, 64))
    def test_name_value(self, value, is_valid):
        """
        checks the server-side validation for the project name field

        :param value: tested value for the project name
        :param is_valid: True if such a value is expected to be valid, False if the value is expected to be invalid
        :return: nothing
        """
        self._test_field_value("name", "no_name", value, is_valid, True, value)

    def test_name_required(self):
        """
        Checks whether the project name is required field

        :return: nothing
        """
        self._test_field_required("name", "no_name", True, True, None)

    def test_name_duplicated(self):
        """
        Tests whether the client may create two projects with the same name

        :return: nothing
        """
        path = self.get_entity_list_path()
        headers = self.get_authorization_headers("superuser")
        create_first_project_response = self.client.post(path, data=self.new_root_group_data, format="json",
                                                         **headers)
        self.assertEquals(create_first_project_response.status_code, status.HTTP_201_CREATED,
                          "The first project shall be successfully created")
        another_project_data = self.no_name_data.copy()
        another_project_data["name"] = create_first_project_response.data["name"]
        create_second_project_response = self.client.post(path, data=another_project_data, format="json",
                                                          **headers)
        self.check_response_duplication_error(create_second_project_response)

    def test_name_duplicated_change(self):
        """
        Checks whether the client may change the name of the project to the existent one

        :return: nothing
        """
        create_path = self.get_entity_list_path()
        headers = self.get_authorization_headers("superuser")
        create_first_project_response = self.client.post(create_path, data=self.new_root_group_data, format="json",
                                                         **headers)
        self.assertEquals(create_first_project_response.status_code, status.HTTP_201_CREATED,
                          "The first project shall be created successfully during this test")
        second_project_data = self.no_name_data.copy()
        second_project_data['name'] = "Some project name"
        create_second_project_response = self.client.post(create_path, data=second_project_data, format="json",
                                                          **headers)
        self.assertEquals(create_second_project_response.status_code, status.HTTP_201_CREATED,
                          "The second project shall be created successfully during this test")
        project_modification_path = self.get_entity_detail_path(create_second_project_response.data['id'])
        project_modification_data = {"name": create_first_project_response.data["name"]}
        project_modification_response = self.client.patch(project_modification_path,
                                                          data=project_modification_data, format="json", **headers)
        self.check_response_duplication_error(project_modification_response)

    @parameterized.expand(arbitrary_string_provider(True, 1024))
    def test_description_value(self, value, is_valid):
        """
        Checks the project description validation feature at the server side

        :param value:value of the project description
        :param is_valid: True if this value is expected to be valid, False is the value is expected to be invalid
        :return: nothing
        """
        self._test_field_value("description", "new_root_group", value, is_valid, True, value)

    def test_description_required(self):
        """
        Checks whether the description field is required

        :return: nothing
        """
        self._test_field_required("description", "new_root_group", False, True, None)

    def check_response_duplication_error(self, response):
        """
        Checks whether the response notifies the client that duplication error was occured at the server side

        :param response: the response to be explored
        :return: nothing
        """
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST,
                          "The response can't be modified to the existent one")
        self.assertEquals(response.data['code'], "EntityDuplicatedException",
                          "The response body must contain the 'code' field with 'EntityDuplicatedException' value")
