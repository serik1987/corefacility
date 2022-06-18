from datetime import timedelta
from parameterized import parameterized
from rest_framework import status

from core import App as CoreApp
from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.user import UserSet
from core.entity.entity_fields.field_managers.entity_password_manager import EntityPasswordManager
from authorizations.cookie.entity.cookie import CookieSet

from .base_test_class import login_provider, BaseTestClass
from .decorators import enable_single_method, enable_all_methods, disable_all_methods


class TestCookieAuthorization(BaseTestClass):
    """
    Tests the cookie authorization
    """

    _method_alias = "cookie"
    login_response = "/api/{version}/login/".format(version=BaseTestClass.API_VERSION)

    support_user = None
    password = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        alphabet = EntityPasswordManager.SMALL_LATIN_LETTERS + EntityPasswordManager.DIGITS
        max_symbols = CoreApp().get_max_password_symbols()
        cls.support_user = UserSet().get("support")
        cls.password = cls.users['user'].password_hash.generate(alphabet, max_symbols)
        cls.users['user'].update()

    @parameterized.expand(login_provider())
    @enable_single_method
    def test_successful_authorization(self, login):
        """
        Tests for successful cookie authorization

        :param login: user's login
        :return: nothing
        """
        user = self.users[login]
        token = AuthorizationModule.issue_token(user)
        self.assert_profile_response(token, user)
        self.assert_token_ok(user)

    @parameterized.expand(login_provider())
    @enable_all_methods
    def test_multiple_authorization(self, login):
        user = self.users[login]
        token = AuthorizationModule.issue_token(user)
        self.assert_profile_response(token, user)
        self.assert_token_ok(user)

    @enable_single_method
    def test_no_cookie(self):
        """
        Tries to authorize with no cookie

        :return: nothing
        """
        self.assert_token_failed()

    @enable_all_methods
    def test_alternative_authorization(self):
        self.assert_special_token_ok()

    @enable_single_method
    def test_failed_authorization(self):
        """
        Tries to authorize with bad cookie

        :return: nothing
        """
        self.client.cookies.load({"token": "The Bad Token"})
        self.assert_token_failed()

    @enable_all_methods
    def test_ambiguous_authorization(self):
        """
        Tries ambiguous auithorization when one authorization method is OK but another one is failed
        
        :return: nothing
        """
        self.client.cookies.load({"token": "The Bad Token"})
        self.assert_token_failed()

    @parameterized.expand(login_provider())
    @enable_single_method
    def test_expired_cookie(self, login):
        """
        Tries to authorize with expired cookie

        :param login: authorization login
        :return: nothing
        """
        user = self.users[login]
        token = AuthorizationModule.issue_token(user)
        self.assert_profile_response(token, user)
        self.simulate_token_expiration()
        self.assert_token_failed()

    @parameterized.expand(login_provider())
    @enable_all_methods
    def test_ambiguous_expired_cookie(self, login):
        """
        Tries ambiguous authorization when the cookie has been expired

        :return: nothing
        """
        user = self.users[login]
        token = AuthorizationModule.issue_token(user)
        self.assert_profile_response(token, user)
        self.simulate_token_expiration()
        self.assert_token_failed()

    @parameterized.expand(login_provider())
    @enable_single_method
    def test_user_locked(self, login):
        """
        Tests authorization of the locked user using the cookie

        :param login: authorization login
        :return: nothing
        """
        user = self.users[login]
        token = AuthorizationModule.issue_token(user)
        self.assert_profile_response(token, user)
        user.is_locked = True
        user.update()
        self.assert_token_failed()

    @disable_all_methods
    def test_ordinary_page_view(self):
        """
        Tests all authorization methods to be disabled

        :return: nothing
        """
        self.assert_token_failed()

    @enable_all_methods
    def test_authorization_not_authentication(self):
        """
        Checks that the authorization is not authentication

        :return: nothing
        """
        response = self.client.post(self.login_response, data={"login": "user", "password": self.password},
                                    format="json")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        if 'token' in response.cookies:
            self.assertEquals(response.cookies['token'].value, "",
                              "Authorization is not authentication: No cookie shall be sent "
                              "during the API authorization")
        self.assert_profile_response(token, self.users['user'])
        self.assert_token_ok(self.users['user'])

    def simulate_token_expiration(self):
        """
        Imitates expiration of all tokens containing in cookie

        :return: nothing
        """
        delta = -timedelta(hours=1)
        for cookie in CookieSet():
            cookie.expiration_date.set(delta)
            cookie.update()


del BaseTestClass
