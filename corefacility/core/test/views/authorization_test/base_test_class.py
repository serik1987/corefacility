from rest_framework import status
from parameterized import parameterized

from core.entity.user import User, UserSet
from core.entity.entry_points.authorizations import AuthorizationsEntryPoint, AuthorizationModule
from core.views import LoginView

from ..base_view_test import BaseViewTest
from .decorators import enable_single_method, enable_all_methods


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

    @parameterized.expand(login_provider())
    @enable_single_method
    def test_successful_authorization(self, login):
        """
        Provides positive authorization test

        :param login: login for a user trying to be authorized
        :return: nothing
        """
        data = self.get_authorization_data(login, is_test_positive=True)
        response = self.client.post(self.authorization_path, data=data, format="json")
        self.assert_authorization_success(login, response)

    @parameterized.expand(login_provider())
    @enable_all_methods
    def test_multiple_authorization(self, login):
        """
        Tests whether this authorization method is still perfect when all available methods were enabled simultaneously

        :param login: login for the authorized user
        :return: nothing
        """
        data = self.get_authorization_data(login, is_test_positive=True)
        response = self.client.post(self.authorization_path, data=data, format="json")
        self.assert_authorization_success(login, response)

    @parameterized.expand(login_provider())
    @enable_single_method
    def test_fail_authorization(self, login):
        """
        Provides fail authorization

        :param login: login for the authorized user
        :return: nothing
        """
        data = self.get_authorization_data(login, is_test_positive=False)
        response = self.client.post(self.authorization_path, data=data, format="json")
        self.assert_authorization_fail(response)

    @parameterized.expand(login_provider())
    @enable_all_methods
    def test_alternative_authorization_hacking(self, login):
        """
        Tests whether the user can be authorized using invalid credentials when all authorization methods are OK

        :param login: login for authorized user
        :return: nothing
        """
        data = self.get_authorization_data(login, is_test_positive=False)
        response = self.client.post(self.authorization_path, data=data, format="json")
        self.assert_authorization_fail(response)

    @enable_single_method
    def test_invalid_authorization(self):
        """
        Provides an authorization with invalid request body

        :return: nothing
        """
        response = self.client.post(self.authorization_path)
        self.assert_authorization_fail(response)

    @enable_all_methods
    def test_alternative_authorization(self):
        """
        Tests whether this authorization method may inactivate alternative authorization methods

        :return: nothing
        """
        response = self.client.post(self.authorization_path)
        self.assert_authorization_success("support", response)

    @parameterized.expand(login_provider())
    @enable_single_method
    def test_locked_user_authorization(self, login):
        """
        Tests whether locked user can be successfully authorized

        :param login: login for the locked user
        :return: nothing
        """
        user = self.users[login]
        user.is_locked = True
        user.update()
        data = self.get_authorization_data(login, is_test_positive=True)
        response = self.client.post(self.authorization_path, data=data, format="json")
        user.is_locked = False
        user.update()
        self.assert_authorization_fail(response)

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

    def assert_authorization_success(self, login, response):
        """
        Asserts that that user has been successfully authorized and the authorized user corresponds to the
        credentials given by him.

        :param login: Login for an authorized user
        :param response: authorization response
        :return: nothing
        """
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assert_user_info(response.data['user'], self.users[login],
                              "The user has been suddenly entered to the foreign account")
        headers = {"HTTP_AUTHORIZATION": "Token " + response.data['token']}
        if login != "support":
            profile_response = self.client.get(self.profile_path, **headers)
            self.assertEquals(profile_response.status_code, status.HTTP_200_OK,
                              "The authorization method has been returned useless token")
            self.assert_user_info(profile_response.data, self.users[login],
                                  "The authorization method returned a foreign token")

    def assert_authorization_fail(self, response):
        """
        Asserts that the user has been failed the authorization

        :param response: response that shall be indicated about failure
        :return: nothing
        """
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
                      "When authorization fails, the response status code shall be either 401 or 403")
        self.assertIn("detail", response.data, "Undetailed error response")
        self.assertEquals(response.data["code"], "authorization_failed",
                          "The response status is OK but the code of the error is wrong")

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

    def assert_ui_authorization(self, response, expected_user: User):
        """
        Asserts that the authorization was automatically applied during the UI

        :param response: the response itself
        :param expected_user: a user that shall be automatically authorized by this way
        :return: nothing
        """
        token = self.get_token_from_ui_response(response)
        self.assertNotEqual(token, "null", "Authorization token has not been presented")

    def assert_no_ui_authorization(self, response):
        """
        Asserts that the UI response contains no authorization token

        :param response: the response containing a Web page
        :return: nothing
        """
        token = self.get_token_from_ui_response(response)
        self.assertEquals(token, "null", "The authorization token was unexpectedly sent to the client during the UI")


del BaseViewTest
