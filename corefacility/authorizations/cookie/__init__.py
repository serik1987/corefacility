from datetime import timedelta

from django.conf import settings

from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.entity_exceptions import EntityNotFoundException


class App(AuthorizationModule):
    """
    Provides an authorization through the web browser cookie which means the following:

    1) During the first call this method skips the authorization. However, after successful
    authorization it sends Cookie to the user with a special authorization token

    2) Next, if the user sends cookie with this token, it will be authorized automatically
    """

    DEFAULT_COOKIE_LIFETIME = timedelta(days=1)

    def get_alias(self):
        """
        The authorization method alias

        :return: 'cookie'
        """
        return "cookie"

    def get_name(self):
        """
        The authorization method name

        :return: the method name
        """
        return "Authorization through Cookie"

    def get_html_code(self):
        """
        The method doesn't have HTML code because it doesn't require
        additional actions from the user to authorize it

        :return: None, of course
        """
        return None

    def is_enabled_by_default(self):
        """
        False because authorization through Cookie may not be safe

        :return: always False
        """
        return False

    def set_cookie(self, request, response, refresh=False):
        """
        Sets the cookie. The cookie will be used in the following authorizations

        :param request: the HTTP request
        :param response: the HTTP response
        :param refresh: True to refresh the cookie expiration term in the database, False otherwise
        :return: nothing
        """
        from .entity.cookie import Cookie
        expiry_term = self.get_cookie_lifetime()
        token = request.get_signed_cookie(settings.COOKIE_NAME, default="", max_age=expiry_term)
        if token and refresh and not hasattr(request, "corefacility_cookie"):
            try:
                token_object = Cookie.apply(token)
                token_object.refresh(expiry_term)
            except EntityNotFoundException:
                token = None
        if not token:
            token = Cookie.issue(request.user, expiry_term)
        response.set_signed_cookie(settings.COOKIE_NAME, token,
                                   max_age=expiry_term.total_seconds(), **settings.COOKIE_FEATURES)

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
        expiry_term = self.get_cookie_lifetime()
        token = request.get_signed_cookie(settings.COOKIE_NAME, default="", max_age=expiry_term)
        if len(token) > 0:
            from .entity.cookie import Cookie
            Cookie.clear_all_expired_tokens()
            try:
                token_object = Cookie.apply(token)
                token_object.refresh(expiry_term)
                user = token_object.user
                request.corefacility_cookie = token
            except EntityNotFoundException:
                pass
        return user

    def try_api_authorization(self, request):
        pass

    def process_auxiliary_request(self, request):
        pass

    def get_cookie_lifetime(self):
        """
        Returns the cookie lifetime

        :return: the cookie lifetime
        """
        return self.user_settings.get("cookie_lifetime", self.DEFAULT_COOKIE_LIFETIME)
