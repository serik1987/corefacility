from django.utils.translation import gettext_lazy as _

from ...entity.entity_sets.user_set import UserSet
from ...exceptions.entity_exceptions import EntityNotFoundException

from ru.ihna.kozhukhov.core_application.modules.auth_login_password import LoginPasswordAuthorization
from ru.ihna.kozhukhov.core_application.modules.auth_standard.serializer import StandardAuthorizationSerializer


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
        return "ru.ihna.kozhukhov.core_application.modules.auth_standard.StandardAuthorization"

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
        _("Standard authorization")
        return "Standard authorization"

    def authorize(self, login: str, password: str):
        """
        Performs an immediate user's authorization

        :param login: user's login
        :param password: user's password
        :return: the user authorized
        """
        try:
            user_set = UserSet()
            user_set.is_locked = False
            user_set.is_support = False
            # The support user can't authorize if authomatic authorization is switched off
            # If authomatic authorization is switched on, the whole method is unreachable
            user = user_set.get(login)
        except EntityNotFoundException:
            return None
        self._throttle_authorization(user)
        if not user.password_hash.check(password):
            self._notify_failed_authorization(user)
            user = None
        return user

    def get_serializer_class(self):
        """
        The settings serializer class transforms module settings to Python primitives and vice versa.
        The module settings serializer can also provide the serialization process
        :return:
        """
        return StandardAuthorizationSerializer

    def get_pseudomodule_identity(self):
        """
        If the module is pseudo-module, the function returns some short string that is required for the frontend to
        identify the pseudo-module.
        :return: a string containing the pseudo-module identity
        """
        return "standard"
