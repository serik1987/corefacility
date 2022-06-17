from parameterized import parameterized
from rest_framework import status

from .base_test_class import login_provider, BaseTestClass
from .decorators import enable_single_method, enable_all_methods


class ApiAuthTest(BaseTestClass):
    """
    A base class for all authorizations that moves through API, not UI
    """

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
        if login != "support":
            self.assert_profile_response(response.data['token'], self.users[login])

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


del BaseTestClass
