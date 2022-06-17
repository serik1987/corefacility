from core import App as CoreApp
from core.entity.entity_fields.field_managers.entity_password_manager import EntityPasswordManager

from .login_password_authorization import LoginPasswordAuthorization


class TestStandardAuthorization(LoginPasswordAuthorization):
    """
    Tests the standard authorization routine
    """

    _method_alias = "standard"

    passwords = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        alphabet = EntityPasswordManager.SMALL_LATIN_LETTERS + EntityPasswordManager.DIGITS
        max_symbols = CoreApp().get_max_password_symbols()
        cls.passwords = {}
        for login, user in cls.users.items():
            if login != "support":
                password = user.password_hash.generate(alphabet, max_symbols)
                user.update()
                cls.passwords[login] = password

    def get_authorization_data(self, login, is_test_positive, **kwargs):
        """
        Returns the tested authorization credentials

        :param login: login for a user trying to be authorized
        :param is_test_positive: True for positive testing, False otherwise
        :param kwargs: some additional arguments specific to a given authorization method
        :return: nothing
        """
        return {
            "login": login,
            "password": self.passwords[login] if is_test_positive else "some_password"
        }


del LoginPasswordAuthorization
