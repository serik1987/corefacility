from rest_framework import status
from parameterized import parameterized

from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.project import ProjectSet
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject

from .base_test_class import BaseTestClass


class ProjectInfo:
    project_alias = None
    access_level = None
    is_user_governor = None

    def __init__(self, project_alias, access_level, is_user_governor):
        self.project_alias = project_alias
        self.access_level = access_level
        self.is_user_governor = is_user_governor


def project_list_provider():
    return [
        (None, status.HTTP_401_UNAUTHORIZED, None),
        ("ordinary_user", status.HTTP_200_OK, []),
        ("superuser", status.HTTP_200_OK, [ProjectInfo(alias, "full", True) for alias in (
            "hhna", "cnl", "mnl", "mn", "nsw", "n", "nl", "gcn", "aphhna", "cr"
        )]),
        ("user1", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", False),
            ProjectInfo("cnl", "full", False),
            ProjectInfo("mnl", "full", False),
            ProjectInfo("mn", "full", False),
        ]),
        ("user2", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", True),
            ProjectInfo("cnl", "full", True),
            ProjectInfo("mnl", "data_full", False),
            ProjectInfo("mn", "data_add", False),
        ]),
        ("user3", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", False),
            ProjectInfo("cnl", "full", False),
            ProjectInfo("mnl", "full", False),
            ProjectInfo("mn", "full", False),
        ]),
        ("user4", status.HTTP_200_OK, [
            ProjectInfo("cnl", "data_process", False),
            ProjectInfo("mnl", "full", True),
            ProjectInfo("mn", "full", True),
            ProjectInfo("nsw", "full", False),
            ProjectInfo("n", "full", False),
        ]),
        ("user5", status.HTTP_200_OK, [
            ProjectInfo("cnl", "data_process", False),
            ProjectInfo("mnl", "full", False),
            ProjectInfo("mn", "full", False),
            ProjectInfo("nsw", "full", True),
            ProjectInfo("n", "full", True),
        ]),
        ("user6", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", False),
            ProjectInfo("cnl", "full", False),
            ProjectInfo("mnl", "data_full", False),
            ProjectInfo("mn", "data_add", False),
            ProjectInfo("nsw", "full", False),
            ProjectInfo("n", "full", False),
            ProjectInfo("nl", "full", False),
            ProjectInfo("gcn", "data_process", False),
        ]),
        ("user7", status.HTTP_200_OK, [
            ProjectInfo("mnl", "data_view", False),
            ProjectInfo("nsw", "full", False),
            ProjectInfo("n", "full", False),
            ProjectInfo("nl", "full", False),
            ProjectInfo("gcn", "full", False),
            ProjectInfo("aphhna", "full", False),
            ProjectInfo("cr", "full", False),
        ]),
        ("user8", status.HTTP_200_OK, [
            ProjectInfo("nsw", "data_add", False),
            ProjectInfo("n", "full", True),
            ProjectInfo("nl", "full", True),
            ProjectInfo("gcn", "full", True),
            ProjectInfo("aphhna", "full", True),
            ProjectInfo("cr", "full", True),
        ]),
        ("user9", status.HTTP_200_OK, [
            ProjectInfo("nsw", "data_add", False),
            ProjectInfo("n", "full", False),
            ProjectInfo("nl", "full", False),
            ProjectInfo("gcn", "full", False),
            ProjectInfo("aphhna", "full", False),
            ProjectInfo("cr", "full", False),
        ]),
        ("user10", status.HTTP_200_OK, [
            ProjectInfo("nl", "data_view", False),
            ProjectInfo("gcn", "full", False),
            ProjectInfo("aphhna", "full", False),
            ProjectInfo("cr", "full", False),
        ])
    ]


def project_retrieve_provider(status_ok, status_fail):
    def preliminary_data_provider(login):
        return [
            (login, alias, status_fail, None, None)
            for alias in ("nsw", "n", "nl", "gcn", "aphhna", "cr")
        ]
    return [
        ("user1", "hhna", status_ok, "full", False),
        ("user1", "cnl", status_ok, "full", False),
        ("user1", "mnl", status_ok, "full", False),
        ("user1", "mn", status_ok, "full", False),
        *preliminary_data_provider("user1"),

        ("user2", "hhna", status_ok, "full", True),
        ("user2", "cnl", status_ok, "full", True),
        ("user2", "mnl", status_ok, "data_full", False),
        ("user2", "mn", status_ok, "data_add", False),
        *preliminary_data_provider("user2"),

        ("user3", "hhna", status_ok, "full", False),
        ("user3", "cnl", status_ok, "full", False),
        ("user3", "mnl", status_ok, "full", False),
        ("user3", "mn", status_ok, "full", False),
        *preliminary_data_provider("user3"),

        ("user4", "hhna", status_fail, None, None),
        ("user4", "cnl", status_ok, "data_process", False),
        ("user4", "mnl", status_ok, "full", True),
        ("user4", "mn", status_ok, "full", True),
        ("user4", "nsw", status_ok, "full", False),
        ("user4", "n", status_ok, "full", False),
        ("user4", "nl", status_fail, None, None),
        ("user4", "gcn", status_fail, None, None),
        ("user4", "aphhna", status_fail, None, None),
        ("user4", "cr", status_fail, None, None),

        ("user5", "hhna", status_fail, None, None),
        ("user5", "cnl", status_ok, "data_process", False),
        ("user5", "mnl", status_ok, "full", False),
        ("user5", "mn", status_ok, "full", False),
        ("user5", "nsw", status_ok, "full", True),
        ("user5", "n", status_ok, "full", True),
        ("user5", "nl", status_fail, None, None),
        ("user5", "gcn", status_fail, None, None),
        ("user5", "aphhna", status_fail, None, None),
        ("user5", "cr", status_fail, None, None),

        ("user6", "hhna", status_ok, "full", False),
        ("user6", "cnl", status_ok, "full", False),
        ("user6", "mnl", status_ok, "data_full", False),
        ("user6", "mn", status_ok, "data_add", False),
        ("user6", "nsw", status_ok, "full", False),
        ("user6", "n", status_ok, "full", False),
        ("user6", "nl", status_ok, "full", False),
        ("user6", "gcn", status_ok, "data_process", False),
        ("user6", "aphhna", status_fail, None, None),
        ("user6", "cr", status_fail, None, None),

        ("user7", "hhna", status_fail, None, None),
        ("user7", "cnl", status_fail, None, None),
        ("user7", "mnl", status_ok, "data_view", False),
        ("user7", "mn", status_fail, None, None),
        ("user7", "nsw", status_ok, "full", False),
        ("user7", "n", status_ok, "full", False),
        ("user7", "nl", status_ok, "full", False),
        ("user7", "gcn", status_ok, "full", False),
        ("user7", "aphhna", status_ok, "full", False),
        ("user7", "cr", status_ok, "full", False),

        ("user8", "hhna", status_fail, None, None),
        ("user8", "cnl", status_fail, None, None),
        ("user8", "mnl", status_fail, None, None),
        ("user8", "mn", status_fail, None, None),
        ("user8", "nsw", status_ok, "data_add", False),
        ("user8", "n", status_ok, "full", True),
        ("user8", "nl", status_ok, "full", True),
        ("user8", "gcn", status_ok, "full", True),
        ("user8", "aphhna", status_ok, "full", True),
        ("user8", "cr", status_ok, "full", True),

        ("user9", "hhna", status_fail, None, None),
        ("user9", "cnl", status_fail, None, None),
        ("user9", "mnl", status_fail, None, None),
        ("user9", "mn", status_fail, None, None),
        ("user9", "nsw", status_ok, "data_add", False),
        ("user9", "n", status_ok, "full", False),
        ("user9", "nl", status_ok, "full", False),
        ("user9", "gcn", status_ok, "full", False),
        ("user9", "aphhna", status_ok, "full", False),
        ("user9", "cr", status_ok, "full", False),

        ("user10", "hhna", status_fail, None, None),
        ("user10", "cnl", status_fail, None, None),
        ("user10", "mnl", status_fail, None, None),
        ("user10", "mn", status_fail, None, None),
        ("user10", "nsw", status_fail, None, None),
        ("user10", "n", status_fail, None, None),
        ("user10", "nl", status_ok, "data_view", False),
        ("user10", "gcn", status_ok, "full", False),
        ("user10", "aphhna", status_ok, "full", False),
        ("user10", "cr", status_ok, "full", False),
        ("user10", "inexistent", status_fail, None, None),
    ]


def project_write_provider(status_ok, status_fail, status_epic_fail):
    def preliminary_provider(user):
        return [
            (user, project_alias, status_epic_fail)
            for project_alias in ("nsw", "n", "nl", "gcn", "aphhna", "cr")
        ]
    return [
        ("user1", "hhna", status_fail),
        ("user1", "cnl", status_fail),
        ("user1", "mnl", status_fail),
        ("user1", "mn", status_fail),
        *preliminary_provider("user1"),

        ("user2", "hhna", status_ok),
        ("user2", "cnl", status_ok),
        ("user2", "mnl", status_fail),
        ("user2", "mn", status_fail),
        *preliminary_provider("user2"),

        ("user3", "hhna", status_fail),
        ("user3", "cnl", status_fail),
        ("user3", "mnl", status_fail),
        ("user3", "mn", status_fail),
        *preliminary_provider("user3"),

        ("user4", "hhna", status_epic_fail),
        ("user4", "cnl", status_fail),
        ("user4", "mnl", status_ok),
        ("user4", "mn", status_ok),
        ("user4", "nsw", status_fail),
        ("user4", "n", status_fail),
        ("user4", "nl", status_epic_fail),
        ("user4", "gcn", status_epic_fail),
        ("user4", "aphhna", status_epic_fail),
        ("user4", "cr", status_epic_fail),

        ("user5", "hhna", status_epic_fail),
        ("user5", "cnl", status_fail),
        ("user5", "mnl", status_fail),
        ("user5", "mn", status_fail),
        ("user5", "nsw", status_ok),
        ("user5", "n", status_ok),
        ("user5", "nl", status_epic_fail),
        ("user5", "gcn", status_epic_fail),
        ("user5", "aphhna", status_epic_fail),
        ("user5", "cr", status_epic_fail),

        ("user6", "hhna", status_fail),
        ("user6", "cnl", status_fail),
        ("user6", "mnl", status_fail),
        ("user6", "mn", status_fail),
        ("user6", "nsw", status_fail),
        ("user6", "n", status_fail),
        ("user6", "nl", status_fail),
        ("user6", "gcn", status_fail),
        ("user6", "aphhna", status_epic_fail),
        ("user6", "cr", status_epic_fail),

        ("user7", "hhna", status_epic_fail),
        ("user7", "cnl", status_epic_fail),
        ("user7", "mnl", status_fail),
        ("user7", "mn", status_epic_fail),
        ("user7", "nsw", status_fail),
        ("user7", "n", status_fail),
        ("user7", "nl", status_fail),
        ("user7", "gcn", status_fail),
        ("user7", "aphhna", status_fail),
        ("user7", "cr", status_fail),

        ("user8", "hhna", status_epic_fail),
        ("user8", "cnl", status_epic_fail),
        ("user8", "mnl", status_epic_fail),
        ("user8", "mn", status_epic_fail),
        ("user8", "nsw", status_fail),
        ("user8", "n", status_ok),
        ("user8", "nl", status_ok),
        ("user8", "gcn", status_ok),
        ("user8", "aphhna", status_ok),
        ("user8", "cr", status_ok),

        ("user9", "hhna", status_epic_fail),
        ("user9", "cnl", status_epic_fail),
        ("user9", "mnl", status_epic_fail),
        ("user9", "mn", status_epic_fail),
        ("user9", "nsw", status_fail),
        ("user9", "n", status_fail),
        ("user9", "nl", status_fail),
        ("user9", "gcn", status_fail),
        ("user9", "aphhna", status_fail),
        ("user9", "cr", status_fail),

        ("user10", "hhna", status_epic_fail),
        ("user10", "cnl", status_epic_fail),
        ("user10", "mnl", status_epic_fail),
        ("user10", "mn", status_epic_fail),
        ("user10", "nsw", status_epic_fail),
        ("user10", "n", status_epic_fail),
        ("user10", "nl", status_fail),
        ("user10", "gcn", status_fail),
        ("user10", "aphhna", status_fail),
        ("user10", "cr", status_fail),
        ("user10", "inexistent", status_epic_fail),
    ]


def project_update_provider():
    return [
        (update_method, *args)
        for update_method in ("put", "patch")
        for args in project_write_provider(status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
    ]


def project_search_provider():
    return [
        (search_substring, profile_name)
        for search_substring in ("Нейроонтогенез", "Нейро", "", None, "Название несуществующего проекта")
        for profile_name in ("basic", "light")
    ]


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
