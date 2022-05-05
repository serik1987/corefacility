from parameterized import parameterized
from rest_framework import status

from core.entity.user import UserSet

from .base_test_class import BaseTestClass
from .data_providers import slug_provider, arbitrary_string_provider, boolean_provider


class TestUser(BaseTestClass):
    """
    Provides user field validation tests.

    Any user has the following fields:
    (1) User name (login)
    (2) Password
    (3) Name
    (4) Surname
    (5) E-mail
    (6) Phone
    (7) List of user groups: not in this file!
    (8) Is user locked?
    (9) Superuser status.
    (10) Is user support.
    (11) Whether the user has been authenticated?
    (12) User avatar
    (13) User's UNIX group
    (14) User's home directory
    """

    resource_name = "users"

    no_login_data = {"name": "Иван", "surname": "Иванов"}
    login_data = {"login": "ivan_ivanov", "name": "Иван", "surname": "Иванов"}
    login_only_data = {"login": "ivan_ivanov"}

    def test_login_required(self):
        """
        Checks whether the loging field is required.

        :return: nothing
        """
        self._test_field_required("login", "no_login", True, True, "ivan_ivanov")

    @parameterized.expand(slug_provider(100))
    def test_login(self, initial_value, is_valid):
        """
        Checks a certain value for a login field

        :param initial_value: an initial value to test
        :param is_valid: True if the field is valid, False otherwise
        :return: nothing
        """
        self._test_field_value("login", "no_login", initial_value, is_valid, True, initial_value)

    def test_login_duplicated(self):
        path = self.get_entity_list_path()
        auth = self.get_superuser_authorization()
        response = self.client.post(path, data=self.login_only_data, **auth)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED,
                          "The instance must be created successfully at this test")
        other_response = self.client.post(path, data=self.login_only_data, **auth)
        self.assertEquals(other_response.status_code, status.HTTP_400_BAD_REQUEST,
                          "The user adding response shall be 400 (BAD REQUEST) on entity duplicate")
        self.assertIn("code", other_response.data, "The response code must exist for entity duplicate")
        self.assertEquals(other_response.data["code"], "EntityDuplicatedException",
                          "The response code must be 'EntityDuplicatedException' on entity duplicate")

    def test_password_not_set(self):
        """
        Checks whether the password was initially cleared

        :return: nothing
        """
        path = self.get_entity_list_path()
        auth = self.get_superuser_authorization()
        response = self.client.post(path, data=self.login_data, **auth)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED,
                          "The user shall be created successfully at this test")
        self.assertFalse(response.data["is_password_set"], "By default, the user password shall be cleared")
        output_path = self.get_entity_detail_path(response.data['id'])
        output_response = self.client.get(output_path, **auth)
        self.assertEquals(output_response.status_code, status.HTTP_200_OK,
                          "The response shall be revealed at this stage")
        self.assertFalse(output_response.data['is_password_set'], "By default, the password shall be cleared")

    def test_password_set(self):
        """
        Checks whether the password has been set

        :return: nothing
        """
        input_path = self.get_entity_list_path()
        auth = self.get_superuser_authorization()
        input_response = self.client.post(input_path, data=self.login_data, **auth)
        self.assertEquals(input_response.status_code, status.HTTP_201_CREATED,
                          "The user shall be created successfully at this test")
        output_path = self.get_entity_detail_path(input_response.data['id'])
        password_set_path = output_path + "password-reset/"
        password_response = self.client.post(password_set_path, data={}, **auth)
        self.assertEquals(password_response.status_code, status.HTTP_200_OK,
                          "The password reset function must be OK")
        self.assertIn("password", password_response.data,
                      "The password reset response shall contain the 'password' field")
        password = password_response.data['password']
        output_response = self.client.get(output_path, **auth)
        self.assertEquals(output_response.status_code, status.HTTP_200_OK,
                          "The response shall be successfully retrieved after password set")
        self.assertTrue(output_response.data['is_password_set'],
                        "The password must be turned to SET stage after password set")
        user = UserSet().get(input_response.data['id'])
        check_result = user.password_hash.check(password)
        self.assertTrue(check_result, "The password has been lost during the password set")

    def test_name_required(self):
        self._test_field_required("name", "login_only", False, True, None)

    @parameterized.expand(arbitrary_string_provider(True, 100) + [
        ("Абдурахманганджи", True),
    ])
    def test_name(self, value, is_valid):
        self._test_field_value("name", "login_only", value, is_valid, True, value)

    def test_surname_required(self):
        self._test_field_required("surname", "login_only", False, True, None)

    @parameterized.expand(arbitrary_string_provider(True, 100) + [
        ("Христорождественский-Космодемьянский", True),
        ("Wolfeschlegelsteinhausenbergerdorff", True),
    ])
    def test_surname(self, value, is_valid):
        self._test_field_value("surname", "login_only", value, is_valid, True, value)

    def test_email_required(self):
        self._test_field_required("email", "login", False, True, None)

    @parameterized.expand([
        ("", True),
        ("mail@host.ru", True),
        ("mail@host", False),
        ("sergei.kozhukhov@ihna.ru", True),
        ("sergei_kozhukhov@ihna.ru", True),
        ("sergei-kozhukhov@my-mail.online", True),
        ("мой-аккаунт@домен.рф", False),
        ("my-account", False),
        ("my-account@ihna-ru", False),
    ])
    def test_email(self, value, is_valid):
        self._test_field_value("email", "login", value, is_valid, True, value)

    def test_phone_required(self):
        self._test_field_required("phone", "login", False, True, None)

    @parameterized.expand([
        ("", True),
        ("123", True),
        ("+70000000000", True),
        ("+7 000 000 00 00", True),
        ("+7(000)000-00-00", True),
        ("+7(000) 000 - 0000", True),
        ("kughffd", False),
        ("http:123", False),
        ("+7 123 fkllf", False),
    ])
    def test_phone(self, value, is_valid):
        self._test_field_value("phone", "login", value, is_valid, True, value)

    def test_is_locked_required(self):
        self._test_field_required("is_locked", "login", False, True, False)

    @parameterized.expand(boolean_provider())
    def test_is_locked(self, value, is_valid):
        self._test_field_value("is_locked", "login", value, is_valid, True, value)

    def test_is_superuser_required(self):
        self._test_field_required("is_superuser", "login", False, True, False)

    @parameterized.expand(boolean_provider())
    def test_is_superuser(self, value, is_valid):
        self._test_field_value("is_superuser", "login", value, is_valid, True, value)

    def test_is_support(self):
        self._test_read_only_field("is_support", "login", False)

    def test_avatar(self):
        self._test_read_only_field("avatar", "login", "/static/core/user.svg")


del BaseTestClass
