from datetime import timedelta
import json
import base64
from urllib.parse import urlencode
from urllib3 import PoolManager
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ...entry_points.authorizations import AuthorizationModule
from ...exceptions.entity_exceptions import EntityNotFoundException, AuthorizationException


class App(AuthorizationModule):
    """
    Provides the authorization through the MAIL.RU system
    """
    AUTHORIZATION_CODE_URI = "https://oauth.mail.ru/login/"
    AUTHORIZATION_TOKEN_URI = "https://oauth.mail.ru/token"
    AUTHORIZATION_USER_INFO = "https://oauth.mail.ru/userinfo"
    ID_SYMBOLS = 19
    MAXIMUM_AUTHORIZATION_SESSION_SYMBOLS = 13

    __poolManager = None

    @staticmethod
    def get_pool_manager():
        if App.__poolManager is None:
            App.__poolManager = PoolManager()
        return App.__poolManager

    def get_alias(self):
        """
        Returns the authorization method alias

        :return: always 'mailru'
        """
        return "mailru"

    def get_name(self):
        """
        Returns the authorization method name.
        The method name will always be displayed in the settings window and as
        tooltip for the login window

        :return: the authorization method name.
        """
        _("Authorization through Mail.ru")
        return "Authorization through Mail.ru"

    def get_html_code(self):
        """
        The icon related to this authorization method is always a <div>
        with two standard CSS classes defined in the 'core' module

        :return: the method HTML code
        """
        return "<div class='auth mailru'></div>"

    def is_enabled_by_default(self):
        """
        By default, this method is disabled because one requires it to be properly configured

        :return: always False
        """
        return False

    def get_user_settings(self, user):
        """
        If there is a widget for a module, this method shall return all settings that shall be adjusted personally
        for each user
        :param user: identity which settings shall be returned
        :return: settings to be adjusted personally for each user. Contains a dictionary with the following keys
            'values' a dictionary like settings_name => settings_value
            'description' a dictionary like settings_name => human-readable settings description
        """
        try:
            from ru.ihna.kozhukhov.core_application.modules.auth_mailru.entity import AccountSet
            account_set = AccountSet()
            account_set.user = user
            account = account_set[0]
            data = {
                'values': {
                    'email': account.email,
                }
            }
        except EntityNotFoundException:
            data = {
                'values': {
                    'email': None
                }
            }
        data['description'] = {
            'email': _("User's email in the Mail.Ru mailbox"),
        }
        return data

    def get_user_settings_serializer_class(self, user):
        """
        Returns the serializer object that allows to validate the user settings
        :param user: identity which serializer must be returned
        :return: the validation object
        """
        from .serializers import UserSettingsSerializer
        return UserSettingsSerializer

    def set_user_settings(self, user, settings):
        """
        Adjusts all module settings created personally for a given particular user
        :param user: a user for which settings should be adjusted
        :param settings: settings to be adjusted
        :return: nothing
        """
        try:
            from ru.ihna.kozhukhov.core_application.modules.auth_mailru.entity import AccountSet
            account_set = AccountSet()
            account_set.user = user
            account = account_set[0]
            account.email = settings['email']
            account.update()
        except EntityNotFoundException:
            from ru.ihna.kozhukhov.core_application.modules.auth_mailru.entity import Account
            account = Account(user=user, email=settings['email'])
            account.create()

    def process_auxiliary_request(self, request):
        """
        Executes when the user presses "Authorize via Mail.ru" button.
        The main goal is to redirect to the main page
        :param request: the request received from the client
        :return: redirection URI
        """
        return self.AUTHORIZATION_CODE_URI + '?' + urlencode({
            'client_id': self.get_client_id(),
            'response_type': 'code',
            'scope': 'userinfo',
            'redirect_uri': self.get_base_uri(request),
            'state': self.get_state(request),
            'prompt_force': '1'
        })

    def try_ui_authorization(self, request, view):
        """
        Executes when the Mail.Ru service redirects back to the web site
        :param request: the request received from the Web browser
        :param view: the MainWindow view that has called this method
        :return: nothing
        """
        route = self.restore_state(request, request.GET.get('state'))
        if route is None:
            return None
        if 'error' in request.GET:
            error = request.GET['error']
            if error == 'access_denied':
                raise AuthorizationException(route,
                                             _("To authorize through the Mail.Ru you need to grant a read-only " +
                                               "access to your personal details"))
        if 'code' not in request.GET:
            raise AuthorizationException(route, _("Authorization code did not received from the Mail.Ru server"))

        token_authorization = "Basic " + \
            base64.b64encode(('%s:%s' % (self.get_client_id(), self.get_client_secret()))
                             .encode('utf-8')).decode('utf-8')

        token_response = \
            self.request_oauth2(route,
                                'POST',
                                self.AUTHORIZATION_TOKEN_URI,
                                headers={
                                    'Authorization': token_authorization,
                                    'User-Agent': 'corefacility',   # Fixed 'missing user agent' error
                                },
                                body=urlencode({
                                    'code': request.GET['code'],
                                    'grant_type': 'authorization_code',
                                    'redirect_uri': self.get_base_uri(request)
                                }))
        access_token = token_response['access_token']

        user_info = self.request_oauth2(route, 'GET',
                                        self.AUTHORIZATION_USER_INFO + '?' + urlencode({'access_token': access_token}))

        try:
            from .entity import AccountSet
            account = AccountSet().get(user_info['email'])
        except EntityNotFoundException:
            raise AuthorizationException(route,
                                         _("Your mail.ru account has not been attached to your corefacility account." +
                                           " Please, login using another authorization method and "
                                           "attach your mail.ru account to your corefacility account "
                                           "in your profile settings"))
        view.split_application_path(route)
        return account.user

    def try_api_authorization(self, request):
        pass

    def request_oauth2(self, route, *args, **kwargs):
        """
        Sends the HTTP request to the external authorization service using the urllib3 pool manager
        :param route: the redirection route
        :param args: arguments to pass to the PoolManager.request
        :param kwargs: keyword arguments to pass to the PoolManager.request
        :return: the response body for success.
        """
        manager = self.get_pool_manager()
        response = manager.request(*args, **kwargs)
        try:
            body = json.loads(response.data)
        except json.JSONDecodeError:
            body = {}
        if response.status == status.HTTP_401_UNAUTHORIZED:
            raise AuthorizationException(route, "This application was unabled to be authorized on the Mail.Ru server." +
                                         " Please, check that both client ID and client secret are correct")
        if 'error' in body and 'error_code' in body and 'error_description' in body:
            raise AuthorizationException(route,
                                         "Authorization code verification failed: " + body['error_description'])
        return body

    def get_client_id(self):
        """
        Returns the application client ID. You can receive the application client ID upon registration on the Mail.Ru
        service.
        """
        client_id = self.user_settings.get('client_id', None)
        if client_id is None:
            raise ImproperlyConfigured("The client ID was not set")
        return client_id

    def get_client_secret(self):
        """
        Returns the application client secret. You can receive the Client Secret upon registration on the Mail.Ru
        service.
        """
        client_secret = self.user_settings.get('client_secret', None)
        if client_secret is None:
            raise ImproperlyConfigured("The Client Secret was not set")
        return client_secret

    def get_serializer_class(self):
        """
        Defines the serializer class. The serializer class is used to represent module settings in JSON format
        :return: instance of rest_framework.serializers.Serializer class
        """
        from .serializers import ModuleSerializer
        return ModuleSerializer

    def get_pseudomodule_identity(self):
        """
        If the module is pseudo-module, the function returns some short string that is required for the frontend to
        identify the pseudo-module.
        :return: a string containing the pseudo-module identity
        """
        return 'mailru_authorization'

    def is_enableable(self, new_value):
        errors = {}
        if self.user_settings.get('client_id', None) is None:
            errors['client_id'] = _("To turn this field on please, ensure that this is not empty")
        if self.user_settings.get('client_secret', None) is None:
            errors['client_secret'] = _("To turn this field on please, ensure that this is not empty")
        if self.user_settings.get('expiry_term', timedelta(minutes=10)) <= timedelta(0):
            errors['expiry_term'] = _("The authorization process will not work when this value equals to zero")
        if len(errors) > 0:
            raise ValidationError(errors)
