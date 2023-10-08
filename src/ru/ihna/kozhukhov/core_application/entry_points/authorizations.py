import urllib.parse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.core.signing import Signer
from rest_framework.exceptions import ValidationError

from ..entity.corefacility_module import CorefacilityModule
from ..exceptions.entity_exceptions import AuthorizationException
from ru.ihna.kozhukhov.core_application.entity.entry_point import EntryPoint


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
        from .. import App as CoreApp
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
    def issue_token(user, get_token=False):
        """
        Issues authentication token for a particular user

        :param user: a user to which the token must be issued
        :param get_token: True return a tuple containing authentication token and authentication object itself,
            False return just one string containing an authentication token
        :return: see above
        """
        from .. import App
        from ..entity.authentication import Authentication

        expiry_term = App().get_auth_token_lifetime()
        Authentication.clear_all_expired_tokens()
        if get_token:
            token, authentication = Authentication.issue(user, expiry_term, True)
        else:
            token = Authentication.issue(user, expiry_term)
        signed_token = AuthorizationModule.get_signer().sign(token)
        if get_token:
            return signed_token, authentication
        else:
            return signed_token

    @staticmethod
    def apply_token(token: str):
        """
        Recovers the user using the token

        :param token: the token to be used
        :return: a user recovered
        """
        from .. import App
        from ..entity.authentication import Authentication

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

    def is_enableable(self, new_value):
        """
        Checks whether authorization modules can be enabled
        :param new_value: new value
        :return: nothing, ValidationError will be risen in case of failure
        """
        entry_point = AuthorizationsEntryPoint()
        total_modules_enabled = 0
        for _ in entry_point.modules():
            total_modules_enabled += 1
        if total_modules_enabled <= 1 and not new_value:
            raise ValidationError({"is_enabled": gettext("At least one authorization module must be enabled")})

    def get_user_settings(self, user):
        """
        If there is a widget for a module, this method shall return all settings that shall be adjusted personally
        for each user
        :param user: identity which settings shall be returned
        :return: a dictionary with the following fields:
            'values': a dictionary like settings name => settings value
            'description': a dictionary like settings name => settings description
        """
        raise NotImplementedError("get_user_settings")

    def get_user_settings_serializer_class(self, user):
        """
        Returns the serializer object that allows to validate the user settings
        :param user: identity which serializer must be returned
        :return: the validation object
        """
        raise NotImplementedError("get_user_settings_serializer_class")

    def set_user_settings(self, user, settings):
        """
        Adjusts all module settings created personally for a given particular user
        :param user: a user for which settings should be adjusted
        :param settings: settings to be adjusted
        :return: nothing
        """
        raise NotImplementedError("set_user_settings")

    def try_ui_authorization(self, request, view):
        """
        Performs the UI authorization.
        The UI authorization will be performed automatically during the UI application loading. The authorization
        routine will generate authentication token for a particular user and send it as AUTHORIZATION_TOKEN
        Javascript constant.

        :param request: The HTTP request that shall be authorized.
        :param view: the MainWindow view. You can adjust settings view upon the authorization process
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

        :param request: the request received from the Web browser. request.session_id contains unique session ID that
            avoid confuse between different authorization sessions
        :return: redirection URL
        """
        raise NotImplementedError("AuthorizationModule.process_auxiliary_request")

    def get_state(self, request):
        """
        Returns the URL-encoded authorization state. The authorization state is a string that is needed to fully restore
        the authorization session after redirection to the external source (i.e., Google or Mail.Ru).
        Such state contains the following information:
        (a) unique session ID. Such an ID also contains in cookie so the session ID can be used to avoid confusion
        between two different authorization sessions. Also, unique session ID is highly recommended by the mail.ru
        authorization service
        (b) alias of the authorization module. Shall be used to prevent confusions created by two different
        authorization modules
        (c) client route to which the application must be redirected
        (c) client route to which the application must be redirected
        :param request: the HttpRequest object received from the client application
        :return: a string that you shall transmit to the external authorization service and which external authroization
        service shall transmit to you.
        """
        return urllib.parse.urlencode({
            'session': request.session_id,
            'module': self.get_alias(),
            'route': request.GET['route'],
        })

    def restore_state(self, request, state):
        """
        Restores the authorization state created by in the previous authorization request
        :param request: current request received from the Web browser
        :param state: authorization state created in the previous request
        :return: In case of successful authorization session recovery - a string containing the route restores in the
        session. In case when the state doesn't belong to a given authorization module or is not provided in the
        request query params - None. Otherwise, an error will be thrown
        """
        session_properties = {key: value[0] for key, value in urllib.parse.parse_qs(state).items()}
        if 'module' in session_properties and session_properties['module'] == self.get_alias():
            if 'route' in session_properties:
                route = session_properties['route']
            else:
                route = None
            expected_session_id = session_properties['session']
            actual_session_id = request.COOKIES.get(self.get_alias())
            if expected_session_id != actual_session_id:
                raise AuthorizationException(route, _("Bad session ID"))
            return route
