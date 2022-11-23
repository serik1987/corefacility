from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.user import UserSet


class AutomaticAuthorization(AuthorizationModule):
    """
    The module requires no information from the user and no cookie from the Web browser and do the
    following (of course, if and only if this method is enabled):
    - if 'support' user account is locked authorization fails;
    - if at least one other authorization method is enabled authorization fails;
    - in any other case the authorization is success

    This method is suitable for 'simple desktop' and 'extended desktop' configuration profile
    when one person only uses the application and hence there is no necessity to provide credentials.
    """

    @property
    def app_class(self):
        """
        The module class
        """
        return "core.authorizations.AutomaticAuthorization"

    def get_alias(self):
        """
        The method alias

        :return: the method alias
        """
        return "auto"

    def get_name(self):
        """
        The method name

        :return: the method name
        """
        _("Automatic authorization")
        return "Automatic authorization"

    def get_html_code(self):
        """
        If this method is enabled and the user passes the authorization a main window will be given,
        the login form will not be presented. Hence, no additional HTML code is required for this
        authorization method

        :return: None
        """
        return None

    def is_enabled_by_default(self):
        """
        The method is enabled immediately after installation because nobody can login in any other way.
        When the superuser is logged in using this method he must create his own account, turn on
        the standard authorization method, turn off this authorization method, lock the 'support' account
        and reload the browser window

        :return: True
        """
        return True

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
        user = None
        cookie_name = settings.COOKIE_NAME
        if cookie_name not in request.COOKIES or len(request.COOKIES[cookie_name]) == 0:
            user = self.authorize_support_user(request)
        return user

    def try_api_authorization(self, request):
        """
        Performs the API authorization.
        The API authorization will be performed manually when the client send '/api/login/' request to the server.
        This function shall process the request and find an appropriate user. There is not neccessity to generate
        authentication token for this particular user.

        :param request: REST framework request
        :return: an authorized user in case of successful authorization. None if authorization fails.
        """
        user = None
        if request.data is None or len(request.data) == 0:
            user = self.authorize_support_user(request)
        return user

    def authorize_support_user(self, request):
        """
        Tries to authorize the 'support' user given that there is no conflict with any other users

        :param request: the authorization request (both API and UI authorizations are OK)
        :return: an authorized user in case of successful authorization. None if authorization fails.
        """
        user = UserSet().get("support")
        if user.is_support and not user.is_locked:
            return user
