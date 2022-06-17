from parameterized import parameterized

from core.entity.entry_points.authorizations import AuthorizationModule

from .base_test_class import login_provider, BaseTestClass
from .decorators import enable_single_method, enable_all_methods
from ..page_object import PageObject


class TestCookieAuthorization(BaseTestClass):
    """
    Tests the cookie authorization
    """

    _method_alias = "cookie"

    @parameterized.expand(login_provider())
    @enable_single_method
    def test_test_successful_authorization(self, login):
        user = self.users[login]
        token = AuthorizationModule.issue_token(user)
        response1 = self.assert_profile_response(token, user)
        window_response = self.client.get("/")
        window_page = PageObject(self, window_response)
        token = window_page.get_option("authorization_token")
        response2 = self.assert_profile_response(token, user)
        print(response1.cookies)
        print(window_response.cookies)
        print(response2.cookies)


del BaseTestClass
