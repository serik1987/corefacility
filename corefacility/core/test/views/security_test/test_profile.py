import json
from rest_framework import status
from parameterized import parameterized

from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.user import UserSet

from .base_test_class import BaseTestClass


def profile_set_provider():
    """
    Returns the tested data for PUT/PATCH requests

    :return: list of argument tuples
    """
    return [
        (None, "nobody@ihna.ru", "+7 000 000 00 00", status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", "ordinary@ihna.ru", "+7 000 000 00 01", status.HTTP_200_OK),
        ("superuser", "superuser@ihna.ru", "+7 000 000 00 02", status.HTTP_200_OK),
        ("support", "support@ihna.ru", "+7 000 000 00 03", status.HTTP_403_FORBIDDEN)
    ]


class TestProfile(BaseTestClass):
    """
    Tests the profile update/retrieve
    """

    PROFILE_REQUEST = "/api/{version}/profile/".format(version=BaseTestClass.API_VERSION)

    superuser_required = True
    ordinary_user_required = True

    support_token = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        support_user = UserSet().get("support")
        cls.support_token = AuthorizationModule.issue_token(support_user)

    @parameterized.expand([
        (None, None, None, None, status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", "user", "User", "Userov", status.HTTP_200_OK),
        ("superuser", "superuser", "Superuser", "Superuserov", status.HTTP_200_OK),
        ("support", "support", None, None, status.HTTP_403_FORBIDDEN)
    ])
    def test_profile_retrieve(self, token_id, login, name, surname, expected_response):
        """
        Checks the user profile retrieve

        :param token_id: token ID. The authorization token itself shall contain in a public property which
            name is composed by attaching the "_token" suffix to the token ID
        :param login: expected login
        :param name: expected first name
        :param surname: expected surname
        :param expected_response: expected response code
        :return: nothing
        """
        auth = self.get_authorization_headers(token_id)
        response = self.client.get(self.PROFILE_REQUEST, **auth)
        self.assertEquals(response.status_code, expected_response, "Unexpected response status code")
        if response.status_code == status.HTTP_200_OK:
            self.assertIn("id", response.data, "the id field must be presented in the response")
            self.assertIn("login", response.data, "The login field must be presented")
            self.assertIn("name", response.data, "The name field must be presented")
            self.assertIn("surname", response.data, "The surname field must be presented")
            self.assertIn("avatar", response.data, "The avatar field must be presented")
            self.assertIn("email", response.data, "The data field must be presented")
            self.assertIn("phone", response.data, "The phone field must be presented")
            self.assertNotIn("is_locked", response.data, "The is_locked field must be hidden")
            self.assertNotIn("is_superuser", response.data, "The is_superuser field must be hidden")
            self.assertNotIn("is_support", response.data, "The is_support field must be hidden")
            self.assertIn("unix_group", response.data, "The unix_group field must be present")
            self.assertIn("home_dir", response.data, "The home_dir field must be present")
            self.assertEquals(response.data["login"], login, "Unexpected login value")
            self.assertEquals(response.data["name"], name, "Unexpected name value")
            self.assertEquals(response.data["surname"], surname, "Unexpected surname value")

    @parameterized.expand(profile_set_provider())
    def test_profile_update(self, token_id, email, phone, expected_status):
        """
        Tests whether the user can fill its profile

        :param token_id: token ID. The authorization token itself shall contain in a public property which
            name is composed by attaching the "_token" suffix to the token ID
        :param email: sample E-mail
        :param phone: sample phone
        :param expected_status: sample status
        :return: nothing
        """
        auth = self.get_authorization_headers(token_id)
        get_response = self.client.get(self.PROFILE_REQUEST, **auth)
        user_info = get_response.data
        user_info['email'] = email
        user_info['phone'] = phone
        user_info = json.dumps(user_info)
        put_response = self.client.put(self.PROFILE_REQUEST, data=user_info, content_type="application/json", **auth)
        self.check_profile_changed(put_response, expected_status, email, phone)

    @parameterized.expand(profile_set_provider())
    def test_profile_partial_update(self, token_id, email, phone, expected_status):
        """
        Tests whether the user can partially update its profile

        :param token_id: token ID. The authorization token itself shall contain in a public property which
            name is composed by attaching the "_token" suffix to the token ID
        :param email: sample E-mail
        :param phone: sample phone
        :param expected_status: sample status
        :return: nothing
        """
        data = {"email": email, "phone": phone}
        auth = self.get_authorization_headers(token_id)
        response = self.client.patch(self.PROFILE_REQUEST, data=data, **auth)
        self.check_profile_changed(response, expected_status, email, phone)

    def check_profile_changed(self, response, expected_status, email, phone):
        """
        Checks whether the profile has been changed correctly. If not, the test fails.

        :param response: the response received during the PUT/PATCH requests
        :param expected_status: response status to be expected
        :param email: E-mail that was recently set
        :param phone: phone that was recently set
        :return: nothing
        """
        self.assertEquals(response.status_code, expected_status, "Unexpected status code")
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            self.assertEquals(response.data["email"], email, "The e-mail was not transmitted correctly")
            self.assertEquals(response.data["phone"], phone, "The phone was not transmitted correctly")
            user_id = response.data["id"]
            user = UserSet().get(user_id)
            self.assertEquals(user.email, email, "The e-mail was not saved correctly")
            self.assertEquals(user.phone, phone, "The phone was not saved correctly")

    @parameterized.expand([
        ("login", "sergei", "user"),
        ("is_locked", True, False),
        ("is_superuser", True, False),
        ("is_support", True, False),
    ])
    def check_field_safety(self, field_name, changing_value, default_value):
        """
        Checks whether some unsafe field has been changed.

        :param field_name: name of the changing field
        :param changing_value: the changing value
        :param default_value: default value
        :return:
        """
        data = {field_name: changing_value}
        auth = self.get_authorization_headers("ordinary_user")
        response = self.client.patch(self.PROFILE_REQUEST, data=data, **auth)
        self.assertEquals(response.status_code, status.HTTP_200_OK,
                          "The response shall be successful according to the current specifications")
        self.assertEquals(response.data[field_name], default_value,
                          "Security check fails: The value has been suddenly changed")
        user = UserSet().get("user")
        self.assertEquals(getattr(user, field_name), default_value,
                          "Security check fails: The value has been suddenly changed")
