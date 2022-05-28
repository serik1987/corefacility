from rest_framework import status
from parameterized import parameterized

from core.entity.group import Group
from core.entity.user import UserSet
from core.entity.entry_points.authorizations import AuthorizationModule

from .base_test_class import BaseTestClass


def standard_test_provider(data_id="sample_entity", ok_status=status.HTTP_201_CREATED):
    return [
        (data_id, None, status.HTTP_401_UNAUTHORIZED),
        (data_id, "ordinary_user", ok_status),
        (data_id, "superuser", ok_status),
    ]


def advanced_test_provider():
    return [
        ("superuser", "superuser", status.HTTP_200_OK),
        ("superuser", "ordinary_user", status.HTTP_200_OK),
        ("ordinary_user", "superuser", status.HTTP_404_NOT_FOUND),
        ("ordinary_user", "ordinary_user", status.HTTP_200_OK),
    ]


def update_provider():
    return [
        (method_name, *args)
        for method_name in ("put", "patch")
        for args in advanced_test_provider()
    ]


class TestGroup(BaseTestClass):
    """
    Provides security test for user group API.
    """

    sample_entity_data = {"name": "Оптическое картирование"}
    updated_entity_data = {"name": "Вазомоторные колебания"}
    governor_data = {"name": "Оптическое картирование"}

    resource_name = "groups"
    _tested_entity = Group
    superuser_required = True
    ordinary_user_required = True
    alias_field = None

    _superuser = None
    _ordinary_user = None
    _another_user = None
    _superuser_group = None
    _ordinary_user_group = None
    _superuser_id = None
    _ordinary_user_id = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._superuser = AuthorizationModule.apply_token(cls.superuser_token)
        cls._ordinary_user = AuthorizationModule.apply_token(cls.ordinary_user_token)
        cls.governor_data['governor'] = cls._ordinary_user
        cls._superuser_group = Group(name="The Superuser Group", governor=cls._superuser)
        cls._superuser_group.create()
        cls._ordinary_user_group = Group(name="The Ordinary User Group", governor=cls._ordinary_user)
        cls._ordinary_user_group.create()
        cls._superuser_id = cls._superuser.id
        cls._ordinary_user_id = cls._ordinary_user.id

    @parameterized.expand(standard_test_provider())
    def test_entity_create(self, data_id, token_id, expected_status_code):
        super()._test_entity_create(data_id, token_id, expected_status_code)

    @parameterized.expand(standard_test_provider())
    def test_entity_security_create(self, data_id, token_id, expected_status_code):
        headers = self.get_authorization_headers(token_id)
        response = self.client.post(self.get_entity_list_path(), data=self.sample_entity_data, format="json",
                                    **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status_code")
        if response.status_code == status.HTTP_201_CREATED:
            user = getattr(self, "_" + token_id)
            self.assert_governors_equal(response, user)

    @parameterized.expand(standard_test_provider(data_id="governor", ok_status=status.HTTP_200_OK))
    def test_entity_get(self, data_id, token_id, expected_status_code):
        self._test_entity_get(data_id, token_id, expected_status_code)

    @parameterized.expand(advanced_test_provider())
    def test_entity_get_advanced(self, token_id, user_id, expected_status_code):
        group = self.get_user_group(user_id)
        path = self.get_entity_detail_path(lookup=group.id)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Status codes are not the same")
        if response.status_code == status.HTTP_200_OK:
            self.assert_governors_equal(response, group.governor)

    @parameterized.expand(update_provider())
    def test_change_name(self, method_name, token_id, user_id, expected_status_code):
        group = self.get_user_group(user_id)
        path = self.get_entity_detail_path(lookup=group.id)
        headers = self.get_authorization_headers(token_id)
        request_func = getattr(self.client, method_name)
        response = request_func(path, data=self.updated_entity_data, format="json", **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        if response.status_code < status.HTTP_400_BAD_REQUEST:
            self.assertEquals(response.data['id'], group.id, "Group IDs are not the same")
            self.assertEquals(response.data['name'], self.updated_entity_data['name'],
                              "Group name has not been written")
            self.assert_governors_equal(response, group.governor)

    def test_group_for_support(self):
        support_user = UserSet().get("support")
        support_token = AuthorizationModule.issue_token(support_user)
        headers = {"HTTP_AUTHORIZATION": "Token " + support_token}
        response = self.client.post(self.get_entity_list_path(), data=self.sample_entity_data,
                                    format="json", **headers)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED,
                          "Failed to create the group from the support user")

    @parameterized.expand(advanced_test_provider())
    def test_user_add_advanced(self, token_id, user_id, expected_status_code):
        group = self.get_user_group(user_id)
        path = self.get_entity_detail_path(group.id) + "users/"
        headers = self.get_authorization_headers(token_id)
        data = {"user_id": getattr(self, "_" + user_id + "_id")}
        response = self.client.post(path, data=data, format="json", **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")

    def check_detail_info(self, actual_info, expected_info):
        """
        Checks whether actual_info contains the same information that exists in the expected_info

        :param actual_info: the actual information
        :param expected_info: the expected information
        :return: nothing
        :except: assertion errors if condition fails
        """
        for key, expected_value in expected_info.items():
            actual_value = self.get_actual_value(actual_info, key)
            if key != "governor":
                self.assertEquals(actual_value, expected_value,
                                  "Necessary values were not stored correctly to the database during the object create")

    def assert_governors_equal(self, response, expected_governor):
        self.assertEquals(response.data['governor']['id'], expected_governor.id,
                          "User IDs are not the same")
        self.assertEquals(response.data['governor']['name'], expected_governor.name,
                          "User names are not the same")
        self.assertEquals(response.data['governor']['surname'], expected_governor.surname,
                          "User surnames are not the same")
        self.assertEquals(response.data['governor']['login'], expected_governor.login,
                          "User logins are not the same")

    def get_user_group(self, user_id):
        return getattr(self, "_{user_id}_group".format(user_id=user_id))


del BaseTestClass
