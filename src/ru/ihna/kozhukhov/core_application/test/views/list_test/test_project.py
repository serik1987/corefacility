from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityNotFoundException
from ru.ihna.kozhukhov.core_application.entry_points.authorizations import AuthorizationModule
from ru.ihna.kozhukhov.core_application.entity.project import ProjectSet

from ...entity_set.entity_set_objects.user_set_object import UserSetObject
from ...entity_set.entity_set_objects.group_set_object import GroupSetObject
from ...entity_set.entity_set_objects.project_set_object import ProjectSetObject
from ...data_providers.api_project_list_provider import *
from .base_test_class import BaseTestClass


class TestProject(BaseTestClass):
    """
    Routines for testing project list API
    """

    resource_name = "projects"
    superuser_required = True
    ordinary_user_required = True

    _request_path = "/api/{version}/projects/".format(version=BaseTestClass.API_VERSION)

    user_container = None
    group_container = None
    project_container = None

    project_update_data = {
        "alias": "tnp",
        "name": "The New Project",
        "description": "Description of The New Project goes here..."
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_containers()
        cls.authorize_all_users()

    @classmethod
    def create_containers(cls):
        cls.user_container = UserSetObject()
        cls.group_container = GroupSetObject(cls.user_container.clone())
        cls.project_container = ProjectSetObject(cls.group_container.clone())

    @classmethod
    def authorize_all_users(cls):
        for user in cls.user_container:
            token = AuthorizationModule.issue_token(user)
            setattr(cls, user.login + "_token", token)

    def setUp(self):
        super().setUp()
        self._container = self.project_container.clone()
        self._container.sort()

    @parameterized.expand(project_list_provider())
    def test_project_list(self, login, expected_status_code, expected_project_list):
        """
        Tests how different users have access to different parts of the project list

        :param login: user's login
        :param expected_status_code: response status code to be expected
        :param expected_project_list: project list to be expected (ProjectInfo objects)
        :return: nothing
        """
        headers = self.get_authorization_headers(login)
        response = self.client.get(self._request_path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status code")
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            actual_project_list = response.data["results"]
            self.assertEquals(len(actual_project_list), len(expected_project_list),
                              "Unexpected number of projects in the project list")
            for item_index in range(len(actual_project_list)):
                actual_project_info = actual_project_list[item_index]
                expected_project_info = expected_project_list[item_index]
                expected_project = self.container.get_by_alias(expected_project_info.project_alias)
                self.assert_items_equal(actual_project_info, expected_project)
                self.assertEquals(actual_project_info['user_access_level'], expected_project_info.access_level,
                                  "Unexpected access level was set to the project")
                self.assertEquals(actual_project_info['is_user_governor'], expected_project_info.is_user_governor,
                                  "Unexpected access level was set to the project")

    @parameterized.expand(project_search_provider())
    def test_project_search(self, search_substring, profile):
        """
        Tests the project search (for superusers only)

        :param search_substring: search substring or None if such an option shall not be used
        :param profile: 'basic' or 'light' pagination profiles
        :return: nothing
        """
        query_params = {"profile": profile}
        if search_substring is not None:
            query_params['q'] = search_substring
            self.container.filter_by_name(search_substring)
        self._test_search(query_params, "superuser", status.HTTP_200_OK)

    @parameterized.expand(project_retrieve_provider(status.HTTP_200_OK, status.HTTP_404_NOT_FOUND))
    def test_project_retrieve(self, login, project_alias, expected_status_code, expected_access_level,
                              expected_is_user_governor):
        """
        Tests for the project retrieve

        :param login: user's login
        :param project_alias: project alias
        :param expected_status_code: status code to be expected
        :param expected_access_level: access level to be expected
        :param expected_is_user_governor: whether the user can modify the project settings or delete the project
        :return: nothing
        """
        path = self.get_entity_detail_path(project_alias)
        headers = self.get_authorization_headers(login)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            project_info = response.data
            self.assertEquals(project_info["alias"], project_alias, "Unexpected project alias")
            self.assertEquals(project_info["user_access_level"], expected_access_level, "Unexpected access level")
            self.assertEquals(project_info["is_user_governor"], expected_is_user_governor,
                              "Unexpected is user governor")

    @parameterized.expand(project_update_provider())
    def test_project_update(self, update_method, token_id, project_alias, expected_status_code):
        """
        Checks for the project ID

        :param update_method: update method: either 'put' or 'patch'
        :param token_id: login of the tested user
        :param project_alias: alias of the project that user is trying to update
        :param expected_status_code: status code to be expected
        :return:
        """
        update_function = getattr(self.client, update_method)
        update_path = self.get_entity_detail_path(project_alias)
        headers = self.get_authorization_headers(token_id)
        response = update_function(update_path, data=self.project_update_data, format="json", **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status code")
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            for key, expected_value in self.project_update_data.items():
                actual_value = response.data[key]
                self.assertEquals(actual_value, expected_value, "Unexpected %s" % key)

    @parameterized.expand(project_write_provider(status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN,
                                                 status.HTTP_404_NOT_FOUND))
    def test_project_destroy(self, token_id, project_alias, expected_status_code):
        """
        Checks whether the project can be destroyed

        :param token_id: ID of the user trying to destroy a project
        :param project_alias: project alias
        :param expected_status_code: expected status code
        :return: nothing
        """
        destroy_path = self.get_entity_detail_path(project_alias)
        headers = self.get_authorization_headers(token_id)
        response = self.client.delete(destroy_path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        project_set = ProjectSet()
        if expected_status_code == status.HTTP_204_NO_CONTENT:
            with self.assertRaises(EntityNotFoundException, msg="The project was not properly deleted"):
                project_set.get(project_alias)
        elif expected_status_code != status.HTTP_404_NOT_FOUND:
            project_set.get(project_alias)

    def assert_items_equal(self, actual_item, desired_item):
        """
        Compares two list item

        :param actual_item: the item received within the response
        :param desired_item: the item taken from the container
        :return: nothing
        """
        self.assertEquals(actual_item['id'], desired_item.id, "Project IDs are not the same")
        self.assertEquals(actual_item['alias'], desired_item.alias, "Project aliases are not the same")
        self.assertEquals(actual_item['avatar'], desired_item.avatar.url, "Project avatars are not the same")
        self.assertEquals(actual_item['name'], desired_item.name, "Project names are not the same"),
        self.assertEquals(actual_item['root_group']['id'], desired_item.root_group.id, "Project root group IDs are "
                                                                                       "not the same")
        self.assertEquals(actual_item['root_group']['name'], desired_item.root_group.name,
                          "Root group names are not the same")


del BaseTestClass
