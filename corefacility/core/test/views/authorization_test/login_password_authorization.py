from core.entity.user import User, UserSet

from .base_test_class import BaseTestClass
from .decorators import enable_single_method, enable_all_methods


class LoginPasswordAuthorization(BaseTestClass):
    """
    This is the base class for testing all authorization methods that require login and password manually entered
    """

    @enable_single_method
    def test_password_empty(self):
        """
        Checks whether we can provide authorization, when the password has not been set by the
        administrator

        :return: nothing
        """
        sample_user = User(login="sample")
        sample_user.create()
        response = self.client.post(self.authorization_path,
                                    data={"login": "sample", "password": ""},
                                    format="json")
        self.assert_authorization_fail(response)

    @enable_single_method
    def test_ui_authorization(self):
        """
        Tests the UI authorization using the single method

        :return: nothing
        """
        response = self.client.get("/")
        self.assert_no_ui_authorization(response)

    @enable_all_methods
    def test_alternative_ui_authorization(self):
        """
        Tests whether UI authorization is possible using alternative methods

        :return: nothing
        """
        response = self.client.get("/")
        self.assert_ui_authorization(response, UserSet().get("support"))


del BaseTestClass
