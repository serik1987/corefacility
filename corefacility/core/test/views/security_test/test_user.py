from rest_framework import status
from parameterized import parameterized

from core.entity.user import User
from core.entity.entry_points.authorizations import AuthorizationModule

from .base_test_class import BaseTestClass


class TestUser(BaseTestClass):
    """
    Security tests for the user list.

    * Each authorized user can view the user list.
    * Listing the detailed user information, add/remove a user and changing user info is allowed for supervisors only.
    """

    resource_name = "users"
    superuser_required = True
    ordinary_user_required = True
    _tested_entity = User
    alias_field = "login"

    ivan_ivanov_token = None
    """ During the object get or set this equals to the token of the object retrieved. """

    test_data = {
        "login": "ivan_ivanov",
        "name": "Иван",
        "surname": "Иванов",
    }

    updated_data = {
        "email": "ivan@ivanov.ru",
        "phone": "+7 000 000 00 00",
    }

    no_data = {}

    @parameterized.expand([
        ("test", None, status.HTTP_401_UNAUTHORIZED),
        ("test", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("test", "superuser", status.HTTP_201_CREATED),
    ])
    def test_entity_create(self, test_data_id, token_id, expected_status_code):
        self._test_entity_create(test_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("test", None, status.HTTP_401_UNAUTHORIZED),
        ("test", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("test", "ivan_ivanov", status.HTTP_403_FORBIDDEN),
        ("test", "superuser", status.HTTP_200_OK)
    ])
    def test_entity_get(self, test_data_id, token_id, expected_status_code):
        """
        Tests the user retrieve function.

        P.S. The user can't change itself by means of '/api/v1/users/login/' path. He must use the
        '/api/v1/profile/' with another permission rules but just only one available account and restricted field
        number.

        :param test_data_id: data ID
        :param token_id: token ID
        :param expected_status_code: expected status code
        :return: nothing
        """
        self._test_entity_get(test_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("test", "updated", None, status.HTTP_401_UNAUTHORIZED),
        ("test", "updated", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("test", "updated", "ivan_ivanov", status.HTTP_403_FORBIDDEN),
        ("test", "updated", "superuser", status.HTTP_200_OK),
        ("test", "no", "superuser", status.HTTP_200_OK),
    ])
    def test_entity_update(self, test_data_id, updated_data_id, token_id, expected_status_code):
        self._test_entity_update(test_data_id, updated_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("test", "updated", None, status.HTTP_401_UNAUTHORIZED),
        ("test", "updated", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("test", "updated", "ivan_ivanov", status.HTTP_403_FORBIDDEN),
        ("test", "updated", "superuser", status.HTTP_200_OK),
        ("test", "no", "superuser", status.HTTP_200_OK),
    ])
    def test_entity_partial_update(self, test_data_id, updated_data_id, token_id, expected_status_code):
        self._test_entity_partial_update(test_data_id, updated_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("test", None, status.HTTP_401_UNAUTHORIZED),
        ("test", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("test", "ivan_ivanov", status.HTTP_403_FORBIDDEN),
        ("test", "superuser", status.HTTP_204_NO_CONTENT),
    ])
    def test_entity_destroy(self, test_data_id, token_id, expected_status_code):
        self._test_entity_destroy(test_data_id, token_id, expected_status_code)

    @parameterized.expand([
        (None, status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", status.HTTP_403_FORBIDDEN),
        ("ivan_ivanov", status.HTTP_403_FORBIDDEN),
        ("superuser", status.HTTP_200_OK),
    ])
    def test_password_set(self, token_id, expected_status_code):
        user = User(**self.test_data)
        user.create()
        self.post_create_routines(user)
        uid = user.id
        path = self.get_entity_detail_path(uid) + "password-reset/"
        auth = self.get_authorization_headers(token_id)
        response = self.client.post(path, data={}, **auth)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")

    def post_create_routines(self, entity):
        """
        This function will be called by _test_entity_get, _test_entity_put, _test_entity_patch immediately after
        the direct entity create

        :param entity: the entity that has been recently created.
        :return: useless
        """
        self.ivan_ivanov_token = AuthorizationModule.issue_token(entity)


del BaseTestClass
