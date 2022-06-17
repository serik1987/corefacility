from core.entity.user import User, UserSet
from core.entity.entity_exceptions import EntityNotFoundException

from .login_password import LoginPasswordAuthorization


class StandardAuthorization(LoginPasswordAuthorization):
    """
    This is a pseudo-module responsible for the standard authorization process

    This is a pseudo-module because it doesn't contain its own database information and API
    but can be configured using the control panel and behaves like any other core authorization
    module
    """

    @property
    def app_class(self):
        """
        Returns the module application class
        """
        return "core.authorizations.StandardAuthorization"

    def get_alias(self):
        """
        The authorization method alias is 'standard'

        :return: 'standard'
        """
        return "standard"

    def get_name(self):
        """
        The authorization method name is always 'Standard authorization'

        :return: always 'Standard authorization'
        """
        return "Standard authorization"

    def authorize(self, login: str, password: str) -> User:
        """
        Performs an immediate user's authorization

        :param login: user's login
        :param password: user's password
        :return: the user authorized
        """
        try:
            user_set = UserSet()
            user_set.is_locked = False
            user = user_set.get(login)
        except EntityNotFoundException:
            return None
        return user if user.password_hash.check(password) else None
