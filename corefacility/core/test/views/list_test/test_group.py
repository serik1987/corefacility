from rest_framework import status
from parameterized import parameterized

from core.entity.entry_points.authorizations import AuthorizationModule
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject

from .base_test_class import BaseTestClass, profile_provider


def security_test_provider():
    return [
        (None, status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", status.HTTP_200_OK),
        ("superuser", status.HTTP_200_OK),
    ] + [
        ("user%d" % user_index, status.HTTP_200_OK) for user_index in range(1, 11)
    ]


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


del BaseTestClass
