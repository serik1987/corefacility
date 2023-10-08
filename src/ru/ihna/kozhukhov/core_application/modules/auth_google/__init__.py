import urllib.parse
from urllib3 import PoolManager

from django.utils.translation import gettext as _
from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import ValidationError

from ...entry_points.authorizations import AuthorizationModule
from ...exceptions.entity_exceptions import EntityNotFoundException, AuthorizationException


class App(AuthorizationModule):
    """
    Provides functionality for authorization from Google Accounts
    """

    AUTHORIZATION_CODE_URI = "https://accounts.google.com/o/oauth2/v2/auth"

    __request = None

    @staticmethod
    def get_pool_manager():
        if App.__poolManager is None:
            App.__poolManager = PoolManager()
        return App.__poolManager

    def get_alias(self):
        """
        The alias is Google

        :return:
        """
        return "google"

    def get_name(self):
        """
        The name is "Authorization through Google"

        :return: the widget name
        """
        return "Authorization through Google"

    def get_html_code(self):
        """
        The icon is <div> with two standard CSS styles
        defined in the 'core' module

        :return: the authorization method icon
        """
        return "<div class='auth google'></div>"

    def is_enabled_by_default(self):
        """
        By default, such method is disabled since it shall be properly adjusted to be enabled

        :return: False
        """
        return False

    def process_auxiliary_request(self, request):
        """
        Calls when the user clicks on the 'Authorize through Google' icon
        :param request: the request received from the Web browser
        :return: URI for the Google login form. The user will be redirected to that form.
        """
        return self.AUTHORIZATION_CODE_URI + '?' + urllib.parse.urlencode({
            'client_id': self.get_client_id(),
            'redirect_uri': self.get_base_uri(request),
            'response_type': 'code',
            'scope': 'email',
            'state': self.get_state(request),
            'access_type': 'offline',
        })

    def try_ui_authorization(self, request, view):
        """
        Calls when the Google authorization page redirects to a given Website
        :param request: the request received from the Web browser
        :param view: the MainWindow view that has invoked this method
        :return: authorized user. Throws an exception when the authorization process fails
        """
        from .entity import AuthorizationToken

        self.__request = request
        route = self.restore_state(request, request.GET.get('state'))
        if route is None:
            return None
        if 'error' in request.GET or 'scope' not in request.GET or \
                'email' not in request.GET['scope'].split(' '):
            raise AuthorizationException(route, _("To authorize through Google you need to provide access of this "
                                                  "application to some personal details stored in Google"))
        token = AuthorizationToken(code=request.GET['code'])
        token.create()

        view.split_application_path(route)
        view.authentication_token = token.authentication_token
        return token.authentication.user

    def try_api_authorization(self, request):
        pass

    def get_serializer_class(self):
        """
        Returns a class responsible for the module settings serializer
        """
        from .serializers import ModuleSettingsSerializer
        return ModuleSettingsSerializer

    def get_pseudomodule_identity(self):
        """
        If the module is pseudo-module, the function returns some short string that is required for the frontend to
        identify the pseudo-module.
        :return: a string containing the pseudo-module identity
        """
        return "google_authorization"

    def get_user_settings(self, user):
        """
        If there is a widget for a module, this method shall return all settings that shall be adjusted personally
        for each user
        :param user: identity which settings shall be returned
        :return: settings to be adjusted personally for each user
        """
        from .entity import AccountSet

        try:
            account_set = AccountSet()
            account_set.user = user
            data = {
                'email': account_set[0].email
            }
        except EntityNotFoundException:
            data = {'email': ''}

        return {
            'values': data,
            'description': {
                'email': _("Google account name (an e-mail)")
            }
        }

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
        from .entity import Account, AccountSet

        try:
            account_set = AccountSet()
            account_set.user = user
            account = account_set[0]
            account.email = settings['email']
            account.update()
        except EntityNotFoundException:
            account = Account(user=user, email=settings['email'])
            account.create()

    def is_enableable(self, new_value):
        """
        Checks whether authorization modules can be enabled
        :param new_value: new value
        :return: nothing, ValidationError will be risen in case of failure
        """
        super().is_enableable(new_value)
        errors = {}
        try:
            self.get_client_id()
        except ImproperlyConfigured:
            errors['client_id'] = _("To enable this module ensure that this field is not empty")
        try:
            self.get_client_secret()
        except ImproperlyConfigured:
            errors['client_secret'] = _("To enable this module ensure that this field is not empty")
        if len(errors) > 0:
            raise ValidationError(errors)

    def get_client_id(self):
        client_id = self.user_settings.get('client_id', None)
        if client_id is None:
            raise ImproperlyConfigured("Client ID was not set correctly")
        return client_id

    def get_client_secret(self):
        client_secret = self.user_settings.get('client_secret', None)
        if client_secret is None:
            raise ImproperlyConfigured("Client Secret was not set correctly")
        return client_secret

    def get_base_uri(self, request):
        request = request or self.__request
        return super().get_base_uri(request)
