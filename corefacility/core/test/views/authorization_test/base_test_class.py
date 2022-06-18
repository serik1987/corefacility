from rest_framework import status

from core.entity.user import User, UserSet
from core.entity.entry_points.authorizations import AuthorizationsEntryPoint, AuthorizationModule
from core.views import LoginView

from ..base_view_test import BaseViewTest
from ..page_object import PageObject


def login_provider():
    return [(login,) for login in ("superuser", "user")]


class BaseTestClass(BaseViewTest):
    """
    This is the base class for all authorization routines
    """

    superuser_required = False
    ordinary_user_required = False

    _method_alias = None
    """ The method alias to be tested """

    users = None
    """ This is a dictionary user_login => user """

    auth_ep = None
    """ Authorization entry point """

    user_info = [
        dict(login="superuser", name="Superuser", surname="Superuserov", is_superuser=True),
        dict(login="user", name="User", surname="Userov", is_superuser=False),
    ]
    """ The user information to use """

    authorization_path = "/api/{version}/login/".format(version=BaseViewTest.API_VERSION)
    profile_path = "/api/{version}/profile/".format(version=BaseViewTest.API_VERSION)
    users_path = "/api/{version}/users/".format(version=BaseViewTest.API_VERSION)
    throttle_classes = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.users = {}
        for user_args in cls.user_info:
            user = User(**user_args)
            user.create()
            cls.users[user.login] = user
        cls.users['support'] = UserSet().get("support")
        cls.auth_ep = AuthorizationsEntryPoint()

    def setUp(self):
        super().setUp()
        self.throttle_classes = LoginView.throttle_classes
        LoginView.throttle_classes = []

    def tearDown(self):
        LoginView.throttle_classes = self.throttle_classes
        super().tearDown()

    @property
    def method_alias(self):
        """
        Method alias to be tested
        """
        if self._method_alias is None:
            raise NotImplementedError("Please, define the _method_alias public property")
        return self._method_alias

    def get_authorization_data(self, login, is_test_positive, **kwargs):
        """
        Returns the tested authorization credentials

        :param login: login for a user trying to be authorized
        :param is_test_positive: True for positive testing, False otherwise
        :param kwargs: some additional arguments specific to a given authorization method
        :return: nothing
        """
        raise NotImplementedError("BaseTestClass.get_authorization_data")

    def assert_token_ok(self, user):
        """
        Asserts that the UI authorization passed successfully and returns a valid authorization token

        :param user: the user that shall be authorized automatically during the loading of the main page
        :return: nothing
        """
        window_response = self.client.get("/")
        window_page = PageObject(self, window_response)
        token = window_page.get_option("authorization_token")
        self.assert_profile_response(token, user)

    def assert_special_token_ok(self):
        """
        Asserts that the UI authorization passed successfully and returns an authorization token corresponding
        to the 'support' user

        :return: nothing
        """
        window_response = self.client.get("/")
        window_page = PageObject(self, window_response)
        token = window_page.get_option("authorization_token")
        self.assertIsNotNone(token, "The authorization token is expected")
        headers = {"HTTP_AUTHORIZATION": "Token " + token}
        response = self.client.get(self.users_path, **headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK, "The special token allows to list all users")
        profile_response = self.client.get(self.profile_path, **headers)
        self.assertEquals(profile_response.status_code, status.HTTP_403_FORBIDDEN,
                          "The special token doesn't allow to view current user's profile")

    def assert_token_failed(self):
        """
        Asserts that the UI authorization doesn't return any authorization token

        :return: nothing
        """
        window_response = self.client.get("/")
        window_page = PageObject(self, window_response)
        token = window_page.get_option("authorization_token")
        self.assertIsNone(token, "The failed token has been passed successfully")

    def assert_user_info(self, actual_info, expected_info: User, msg: str):
        """
        Asserts that the actual user info is the same as expected one

        :param actual_info: actual user info received from the response
        :param expected_info: the expected one
        :param msg: error message when assertion fails
        :return: nothing
        """
        self.assertEquals(actual_info['login'], expected_info.login, msg + ": Unexpected user login")
        self.assertEquals(actual_info['id'], expected_info.id, msg + ": Unexpected user ID")
        self.assertEquals(actual_info['name'], expected_info.name, msg + ": Unexpected user name")
        self.assertEquals(actual_info['surname'], expected_info.surname, msg + ": Unexpected user surname")

    def assert_profile_response(self, token, expected_user):
        """
        Asserts that the profile response is OK with such a token and allows to retrieve the
        data corresponding to the expected_user

        :param token: token that shall be used in trial response
        :param expected_user: the user which the token is expected to belong to
        :return: the profile response
        """
        self.assertIsNotNone(token, "The authorization token is not defined")
        headers = {"HTTP_AUTHORIZATION": "Token " + token}
        profile_response = self.client.get(self.profile_path, **headers)
        self.assertEquals(profile_response.status_code, status.HTTP_200_OK,
                          "The authorization method has been returned useless token")
        self.assert_user_info(profile_response.data, expected_user,
                              "The authorization method returned a foreign token")
        return profile_response


del BaseViewTest
