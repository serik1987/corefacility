from rest_framework import status
from parameterized import parameterized

from core.entity.user import UserSet
from core.entity.group import GroupSet
from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.entry_points.authorizations import AuthorizationModule
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject

from . import security_test_provider
from .base_test_class import BaseTestClass, profile_provider


def security_read_provider():
    return [
        ("user1", 3, status.HTTP_200_OK),
        ("user1", 2, status.HTTP_200_OK),
        ("user1", 4, status.HTTP_404_NOT_FOUND),
        ("user1", 0, status.HTTP_404_NOT_FOUND),
        ("user1", 1, status.HTTP_404_NOT_FOUND),

        ("user2", 3, status.HTTP_200_OK),
        ("user2", 2, status.HTTP_404_NOT_FOUND),
        ("user2", 4, status.HTTP_404_NOT_FOUND),
        ("user2", 0, status.HTTP_404_NOT_FOUND),
        ("user2", 1, status.HTTP_404_NOT_FOUND),

        ("user3", 3, status.HTTP_200_OK),
        ("user3", 2, status.HTTP_200_OK),
        ("user3", 4, status.HTTP_404_NOT_FOUND),
        ("user3", 0, status.HTTP_404_NOT_FOUND),
        ("user3", 1, status.HTTP_404_NOT_FOUND),

        ("user4", 3, status.HTTP_404_NOT_FOUND),
        ("user4", 2, status.HTTP_200_OK),
        ("user4", 4, status.HTTP_200_OK),
        ("user4", 0, status.HTTP_404_NOT_FOUND),
        ("user4", 1, status.HTTP_404_NOT_FOUND),

        ("user5", 3, status.HTTP_404_NOT_FOUND),
        ("user5", 2, status.HTTP_200_OK),
        ("user5", 4, status.HTTP_200_OK),
        ("user5", 0, status.HTTP_404_NOT_FOUND),
        ("user5", 1, status.HTTP_404_NOT_FOUND),

        ("user6", 3, status.HTTP_200_OK),
        ("user6", 2, status.HTTP_404_NOT_FOUND),
        ("user6", 4, status.HTTP_200_OK),
        ("user6", 0, status.HTTP_200_OK),
        ("user6", 1, status.HTTP_404_NOT_FOUND),

        ("user7", 3, status.HTTP_404_NOT_FOUND),
        ("user7", 2, status.HTTP_404_NOT_FOUND),
        ("user7", 4, status.HTTP_200_OK),
        ("user7", 0, status.HTTP_200_OK),
        ("user7", 1, status.HTTP_200_OK),

        ("user8", 3, status.HTTP_404_NOT_FOUND),
        ("user8", 2, status.HTTP_404_NOT_FOUND),
        ("user8", 4, status.HTTP_404_NOT_FOUND),
        ("user8", 0, status.HTTP_200_OK),
        ("user8", 1, status.HTTP_200_OK),

        ("user9", 3, status.HTTP_404_NOT_FOUND),
        ("user9", 2, status.HTTP_404_NOT_FOUND),
        ("user9", 4, status.HTTP_404_NOT_FOUND),
        ("user9", 0, status.HTTP_200_OK),
        ("user9", 1, status.HTTP_200_OK),

        ("user10", 3, status.HTTP_404_NOT_FOUND),
        ("user10", 2, status.HTTP_404_NOT_FOUND),
        ("user10", 4, status.HTTP_404_NOT_FOUND),
        ("user10", 0, status.HTTP_404_NOT_FOUND),
        ("user10", 1, status.HTTP_200_OK),
    ]


def security_write_provider():
    return [
        ("user1", 3, status.HTTP_403_FORBIDDEN),
        ("user1", 2, status.HTTP_403_FORBIDDEN),
        ("user1", 4, status.HTTP_404_NOT_FOUND),
        ("user1", 0, status.HTTP_404_NOT_FOUND),
        ("user1", 1, status.HTTP_404_NOT_FOUND),

        ("user2", 3, status.HTTP_200_OK),
        ("user2", 2, status.HTTP_404_NOT_FOUND),
        ("user2", 4, status.HTTP_404_NOT_FOUND),
        ("user2", 0, status.HTTP_404_NOT_FOUND),
        ("user2", 1, status.HTTP_404_NOT_FOUND),

        ("user3", 3, status.HTTP_403_FORBIDDEN),
        ("user3", 2, status.HTTP_403_FORBIDDEN),
        ("user3", 4, status.HTTP_404_NOT_FOUND),
        ("user3", 0, status.HTTP_404_NOT_FOUND),
        ("user3", 1, status.HTTP_404_NOT_FOUND),

        ("user4", 3, status.HTTP_404_NOT_FOUND),
        ("user4", 2, status.HTTP_200_OK),
        ("user4", 4, status.HTTP_403_FORBIDDEN),
        ("user4", 0, status.HTTP_404_NOT_FOUND),
        ("user4", 1, status.HTTP_404_NOT_FOUND),

        ("user5", 3, status.HTTP_404_NOT_FOUND),
        ("user5", 2, status.HTTP_403_FORBIDDEN),
        ("user5", 4, status.HTTP_200_OK),
        ("user5", 0, status.HTTP_404_NOT_FOUND),
        ("user5", 1, status.HTTP_404_NOT_FOUND),

        ("user6", 3, status.HTTP_403_FORBIDDEN),
        ("user6", 2, status.HTTP_404_NOT_FOUND),
        ("user6", 4, status.HTTP_403_FORBIDDEN),
        ("user6", 0, status.HTTP_403_FORBIDDEN),
        ("user6", 1, status.HTTP_404_NOT_FOUND),

        ("user7", 3, status.HTTP_404_NOT_FOUND),
        ("user7", 2, status.HTTP_404_NOT_FOUND),
        ("user7", 4, status.HTTP_403_FORBIDDEN),
        ("user7", 0, status.HTTP_403_FORBIDDEN),
        ("user7", 1, status.HTTP_403_FORBIDDEN),

        ("user8", 3, status.HTTP_404_NOT_FOUND),
        ("user8", 2, status.HTTP_404_NOT_FOUND),
        ("user8", 4, status.HTTP_404_NOT_FOUND),
        ("user8", 0, status.HTTP_200_OK),
        ("user8", 1, status.HTTP_200_OK),

        ("user9", 3, status.HTTP_404_NOT_FOUND),
        ("user9", 2, status.HTTP_404_NOT_FOUND),
        ("user9", 4, status.HTTP_404_NOT_FOUND),
        ("user9", 0, status.HTTP_403_FORBIDDEN),
        ("user9", 1, status.HTTP_403_FORBIDDEN),

        ("user10", 3, status.HTTP_404_NOT_FOUND),
        ("user10", 2, status.HTTP_404_NOT_FOUND),
        ("user10", 4, status.HTTP_404_NOT_FOUND),
        ("user10", 0, status.HTTP_404_NOT_FOUND),
        ("user10", 1, status.HTTP_403_FORBIDDEN),
    ]


def security_delete_provider():
    def delete_user_provider(token_id, group_index, governor_index):
        dataset = []
        for user_index in range(1, 11):
            status_code = status.HTTP_204_NO_CONTENT if user_index != governor_index else status.HTTP_403_FORBIDDEN
            dataset.append((token_id, group_index, "user%d" % user_index, status_code))
        return dataset
    return [
        *delete_user_provider("superuser", 3, 2),
        *delete_user_provider("superuser", 2, 4),
        *delete_user_provider("superuser", 4, 5),
        *delete_user_provider("superuser", 0, 8),
        *delete_user_provider("superuser", 1, 8),

        ("user1", 3, "user1", status.HTTP_403_FORBIDDEN),
        ("user1", 2, "user3", status.HTTP_403_FORBIDDEN),
        ("user1", 4, "user4", status.HTTP_404_NOT_FOUND),
        ("user1", 0, "user6", status.HTTP_404_NOT_FOUND),
        ("user1", 1, "user10", status.HTTP_404_NOT_FOUND),

        ("user2", 3, "user1", status.HTTP_204_NO_CONTENT),
        ("user2", 2, "user3", status.HTTP_404_NOT_FOUND),
        ("user2", 4, "user4", status.HTTP_404_NOT_FOUND),
        ("user2", 0, "user6", status.HTTP_404_NOT_FOUND),
        ("user2", 1, "user10", status.HTTP_404_NOT_FOUND),

        ("user3", 3, "user1", status.HTTP_403_FORBIDDEN),
        ("user3", 2, "user3", status.HTTP_403_FORBIDDEN),
        ("user3", 4, "user4", status.HTTP_404_NOT_FOUND),
        ("user3", 0, "user6", status.HTTP_404_NOT_FOUND),
        ("user3", 1, "user10", status.HTTP_404_NOT_FOUND),

        ("user4", 3, "user1", status.HTTP_404_NOT_FOUND),
        ("user4", 2, "user3", status.HTTP_204_NO_CONTENT),
        ("user4", 4, "user4", status.HTTP_403_FORBIDDEN),
        ("user4", 0, "user6", status.HTTP_404_NOT_FOUND),
        ("user4", 1, "user10", status.HTTP_404_NOT_FOUND),

        ("user5", 3, "user1", status.HTTP_404_NOT_FOUND),
        ("user5", 2, "user3", status.HTTP_403_FORBIDDEN),
        ("user5", 4, "user4", status.HTTP_204_NO_CONTENT),
        ("user5", 0, "user6", status.HTTP_404_NOT_FOUND),
        ("user5", 1, "user10", status.HTTP_404_NOT_FOUND),

        ("user6", 3, "user1", status.HTTP_403_FORBIDDEN),
        ("user6", 2, "user3", status.HTTP_404_NOT_FOUND),
        ("user6", 4, "user4", status.HTTP_403_FORBIDDEN),
        ("user6", 0, "user6", status.HTTP_403_FORBIDDEN),
        ("user6", 1, "user10", status.HTTP_404_NOT_FOUND),

        ("user7", 3, "user1", status.HTTP_404_NOT_FOUND),
        ("user7", 2, "user3", status.HTTP_404_NOT_FOUND),
        ("user7", 4, "user4", status.HTTP_403_FORBIDDEN),
        ("user7", 0, "user6", status.HTTP_403_FORBIDDEN),
        ("user7", 1, "user10", status.HTTP_403_FORBIDDEN),

        ("user8", 3, "user1", status.HTTP_404_NOT_FOUND),
        ("user8", 2, "user3", status.HTTP_404_NOT_FOUND),
        ("user8", 4, "user4", status.HTTP_404_NOT_FOUND),
        ("user8", 0, "user6", status.HTTP_204_NO_CONTENT),
        ("user8", 1, "user10", status.HTTP_204_NO_CONTENT),

        ("user9", 3, "user1", status.HTTP_404_NOT_FOUND),
        ("user9", 2, "user3", status.HTTP_404_NOT_FOUND),
        ("user9", 4, "user4", status.HTTP_404_NOT_FOUND),
        ("user9", 0, "user6", status.HTTP_403_FORBIDDEN),
        ("user9", 1, "user10", status.HTTP_403_FORBIDDEN),

        ("user10", 3, "user1", status.HTTP_404_NOT_FOUND),
        ("user10", 2, "user3", status.HTTP_404_NOT_FOUND),
        ("user10", 4, "user4", status.HTTP_404_NOT_FOUND),
        ("user10", 0, "user6", status.HTTP_404_NOT_FOUND),
        ("user10", 1, "user10", status.HTTP_403_FORBIDDEN),
    ]


def group_name_provider():
    return [
        (group_name, *other_data)
        for group_name in ["Сёстры Райт", "Райт", "Управляемый хаос", "Управля", "С", "inexistent", ""]
        for other_data in profile_provider()
    ]


class TestGroup(BaseTestClass):
    """
    Tests the user groups
    """

    name_update_data = {"name": "Более приличное название группы..."}

    _user_set_object = None
    _group_set_object = None

    _request_path = "/api/{version}/groups/".format(version=BaseTestClass.API_VERSION)
    _detail_path = "/api/{version}/groups/%d/".format(version=BaseTestClass.API_VERSION)
    _user_list_path = "/api/{version}/groups/%d/users/".format(version=BaseTestClass.API_VERSION)

    superuser_required = True
    ordinary_user_required = True

    superuser = None
    ordinary_user = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_user_set_objects()
        cls.authorize_test_users()
        cls.extract_demo_users()

    @classmethod
    def create_user_set_objects(cls):
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object.clone())

    @classmethod
    def authorize_test_users(cls):
        for user in cls._user_set_object:
            token = AuthorizationModule.issue_token(user)
            setattr(cls, user.login + "_token", token)

    @classmethod
    def extract_demo_users(cls):
        for token_id in ("ordinary_user", "superuser"):
            token = getattr(cls, token_id + "_token")
            user = AuthorizationModule.apply_token(token)
            setattr(cls, token_id, user)

    def setUp(self):
        super().setUp()
        self._container = self._group_set_object.clone()
        self._container.sort()

    @parameterized.expand(security_test_provider())
    def test_security(self, token_id, expected_status_code):
        self.provide_security_filter(token_id)
        self._test_search({"profile": "basic"}, token_id, expected_status_code)

    @parameterized.expand(group_name_provider())
    def test_group_name(self, name, profile):
        query_params = {"q": name, "profile": profile}
        self.container.filter_by_name(name)
        self._test_search(query_params, "superuser", status.HTTP_200_OK)

    @parameterized.expand(security_read_provider())
    def test_group_reveal(self, user_login, group_index, expected_status_code):
        group = self.container[group_index]
        headers = self.get_authorization_headers(user_login)
        path = self._detail_path % group.id
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")

    @parameterized.expand(security_write_provider())
    def test_group_update(self, user_login, group_index, expected_status_code):
        group = self.container[group_index]
        headers = self.get_authorization_headers(user_login)
        path = self._detail_path % group.id
        response = self.client.patch(path, data=self.name_update_data, format="json", **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")

    @parameterized.expand(security_read_provider())
    def test_user_list_read(self, user_login, group_index, expected_status_code):
        group = self.container[group_index]
        path = self._user_list_path % group.id
        headers = self.get_authorization_headers(user_login)
        response = self.client.get(path, **headers)
        self.assert_user_list_response(response, group, expected_status_code)

    @parameterized.expand(security_delete_provider())
    def test_user_list_delete(self, token_id, group_index, delete_user_login, expected_status_code):
        headers = self.get_authorization_headers(token_id)
        group = self.container[group_index]
        request_path = self._detail_path % group.id + "users/%s/" % delete_user_login
        response = self.client.delete(request_path, **headers)
        self.assertEquals(response.status_code, expected_status_code)
        user = self._user_set_object.get_by_alias(delete_user_login)
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            self.assertFalse(group.users.exists(user), "The user still exists in group after delete")
        if status.HTTP_400_BAD_REQUEST <= response.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR:
            self.assertTrue(group.users.exists(user), "The user was suddenly deleted even after request was denied")

    @parameterized.expand(security_read_provider())
    def test_user_suggest(self, token_id, group_index, expected_status_code):
        group = self.container[group_index]
        path = self._detail_path % group.id + "user-suggest/"
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status code")
        user_set = UserSet()
        user_set.is_support = False
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            for actual_user in response.data:
                expected_user = user_set.get(actual_user['id'])
                self.assert_user_equals(actual_user, expected_user)
                self.assertFalse(group.users.exists(expected_user), "The suggested user exists in the group")

    @parameterized.expand(security_write_provider())
    def test_user_list_add(self, token_id, group_index, expected_status_code):
        group = self.container[group_index]
        path = self._detail_path % group.id + "users/"
        headers = self.get_authorization_headers(token_id)
        data = {"user_id": self.ordinary_user.id}
        response = self.client.post(path, data=data, format="json", **headers)
        self.assertEquals(response.status_code, expected_status_code)
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            self.assertTrue(group.users.exists(self.ordinary_user), "The user was not actually added to the user list")
        if status.HTTP_400_BAD_REQUEST <= response.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR:
            self.assertFalse(group.users.exists(self.ordinary_user), "The user was unexpectedly added to the user list")

    @parameterized.expand(security_write_provider())
    def test_delete(self, token_id, group_index, expected_status_code):
        if expected_status_code == status.HTTP_200_OK:
            expected_status_code = status.HTTP_204_NO_CONTENT
        group_id = self.container[group_index].id
        path = self._detail_path % group_id
        headers = self.get_authorization_headers(token_id)
        response = self.client.delete(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        group_set = GroupSet()
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            with self.assertRaises(EntityNotFoundException, msg="The group delete status was ok but"
                                                                "the group still exists"):
                group_set.get(group_id)
        if status.HTTP_400_BAD_REQUEST <= response.status_code < status.HTTP_500_INTERNAL_SERVER_ERROR:
            group_set.get(group_id)

    def provide_security_filter(self, login):
        if login is None:
            return None
        elif hasattr(self, login):
            user = getattr(self, login)
        else:
            user = self._user_set_object.get_by_alias(login)
        if not user.is_superuser:
            self.container.filter_by_user(user)

    def assert_items_equal(self, actual_item, desired_item):
        self.assertEquals(actual_item['id'], desired_item.id, "Item IDs are not the same")
        self.assertEquals(actual_item['name'], desired_item.name, "Item names are not the same")
        self.assertEquals(actual_item['governor']['id'], desired_item.governor.id, "Governor IDs are not the same")
        self.assertEquals(actual_item['governor']['login'], desired_item.governor.login,
                          "Governor login was not transmitted")
        self.assertEquals(actual_item['governor']['name'], desired_item.governor.name,
                          "Governor name was not transmitted")
        self.assertEquals(actual_item['governor']['surname'], desired_item.governor.surname,
                          "Governor surname was not transmitted")

    def assert_user_list_response(self, response, group, expected_status_code):
        """
        Asserts that the actual user list returned by the response is the same as expected user list.
        For responses 2xx actual and desired user lists will be compared one-by-one.

        :param response: the response received by the group user list retrieve request.
        :param group: a group for which the user list is requested
        :param expected_status_code: status code to expect.
        :return: nothing
        """
        self.assertEqual(response.status_code, expected_status_code, "Unexpected user list status code")
        if expected_status_code == status.HTTP_200_OK:
            self.assert_user_list(response.data, group.users)

    def assert_user_list(self, response_output, user_list):
        """
        Asserts that two user lists were equal

        :param response_output: the response body
        :param user_list: expected user list
        :return: nothing
        """
        self.assertEquals(response_output['count'], len(user_list), "Number of users in the user list is not the same "
                                                                    "as expected")
        if response_output['next'] is not None or response_output['previous'] is not None:
            self.skipTest("assert_user_list function doesn't support multi-page responses")
        self.assertEquals(response_output['count'], len(response_output['results']),
                          "The 'count' property of the response doesn't reflect the returned number of items"
                          " in the list")
        for index in range(response_output['count']):
            actual_user = response_output['results'][index]
            desired_user = user_list[index]
            self.assert_user_equals(actual_user, desired_user)

    def assert_user_equals(self, actual_user, desired_user):
        self.assertEquals(actual_user['id'], desired_user.id, "User IDs are not the same")
        self.assertEquals(actual_user['login'], desired_user.login, "User logins are not the same")
        self.assertEquals(actual_user['name'], desired_user.name, "User names are not the same")
        self.assertEquals(actual_user['surname'], desired_user.surname, "User surnames are not the same")


del BaseTestClass
