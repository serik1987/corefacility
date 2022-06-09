from rest_framework import status
from parameterized import parameterized

from core.entity.entry_points.authorizations import AuthorizationModule
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject

from . import security_test_provider
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

    superuser_required = True
    ordinary_user_required = True

    _request_path = "/api/{version}/projects/".format(version=BaseTestClass.API_VERSION)

    user_container = None
    group_container = None
    project_container = None

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
