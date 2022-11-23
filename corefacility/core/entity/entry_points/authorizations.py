from django.utils.translation import gettext_lazy as _
from django.core.signing import Signer

from core.entity import CorefacilityModule
from .entry_point import EntryPoint


class AuthorizationsEntryPoint(EntryPoint):
    """
    The entry point allows you to connect to 'corefacility' additional modules each of this
    can provide various kinds of authorizations: authorization by login and password,
    authorization though Google, authorization through Research Gate and so on.
    """

    _is_parent_module_root = True
    """ The property is used during the autoloading """

    def get_alias(self):
        """
        The entry point alias is also the same

        :return: 'authorizations'
        """
        return "authorizations"

    def get_name(self):
        """
        Provides the entry point name visible in the UI

        :return: the entry point name visible in the UI
        """
        _("Authorization methods")
        return "Authorization methods"

    def get_type(self):
        return "lst"

    def get_parent_module_class(self):
        """
        Returns the parent module for a given entry point. Such a module will be used as an entry point cue

        :return: the parent module or None if no cue shall be provided
        """
        from core import App as CoreApp
        return CoreApp


class AuthorizationModule(CorefacilityModule):
    """
    Defines common methods of all modules attached to the 'authorizations' module.

    This includes not only override of all abstract properties but also contract of
    interaction with the 'core' module
    """

    _signer = None

    @staticmethod
    def get_signer():
        """
        Returns the module signer

        :return: the module signer
        """
        if AuthorizationModule._signer is None:
            AuthorizationModule._signer = Signer()
        return AuthorizationModule._signer

    @staticmethod
    def issue_token(user):
        """
        Issues authentication token for a particular user

        :param user: a user to which the token must be issued
        :return: a string containing an authentication token
        """
        from core import App
        from core.entity.authentication import Authentication

        expiry_term = App().get_auth_token_lifetime()
        Authentication.clear_all_expired_tokens()
        token = Authentication.issue(user, expiry_term)
        signed_token = AuthorizationModule.get_signer().sign(token)
        return signed_token

    @staticmethod
    def apply_token(token: str):
        """
        Recovers the user using the token

        :param token: the token to be used
        :return: a user recovered
        """
        from core import App
        from core.entity.authentication import Authentication

        expiry_term = App().get_auth_token_lifetime()
        unsigned_token = AuthorizationModule.get_signer().unsign(token)
        token_entity = Authentication.apply(unsigned_token)
        token_entity.refresh(expiry_term)
        return Authentication.get_user()

    def get_parent_entry_point(self):
        """
        All authorization applications must be attached to the 'authorizations' entry point

        :return: the parent entry point
        """
        return AuthorizationsEntryPoint()

    @property
    def is_application(self):
        """
        Since authorization modules shall authorize non-authorized user, they are modules, not applications

        :return: always False
        """
        return False

    def try_ui_authorization(self, request):
        """
        Performs the UI authorization.
        The UI authorization will be performed automatically during the UI application loading. The authorization
        routine will generate authentication token for a particular user and send it as AUTHORIZATION_TOKEN
        Javascript constant.

        :param request: The HTTP request that shall be authorized.
        :return: an authorized user in case of successful authorization. None if authorization fails. The function
        shall not generate authorization token, just return the user. The user if core.entity.user.User instance.
        """
        raise NotImplementedError("AuthorizationModule.try_ui_authorization")

    def try_api_authorization(self, request):
        """
        Performs the API authorization.
        The API authorization will be performed manually when the client send '/api/login/' request to the server.
        This function shall process the request and find an appropriate user. There is not neccessity to generate
        authentication token for this particular user.

        :param request: REST framework request
        :return: an authorized user in case of successful authorization. None if authorization fails. The function
        shall not generate authorization token, just return the user. The user if core.entity.user.User instance.
        """
        raise NotImplementedError("AuthorizationModule.try_api_authorization")

    def process_auxiliary_request(self, request):
        """
        Performs an auxiliary request processing.
        The auxiliary request processing is required when the application shall be redirected to the 3rd party site.

        :param request: REST framework request
        :return: redirection URL
        """
        raise NotImplementedError("AuthorizationModule.process_auxiliary_request")
