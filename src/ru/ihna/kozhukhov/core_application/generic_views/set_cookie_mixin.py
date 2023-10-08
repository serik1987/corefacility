from django.conf import settings

from ..entity.user import User
from ..exceptions.entity_exceptions import EntityNotFoundException
from ..entry_points.authorizations import AuthorizationsEntryPoint


class SetCookieMixin:
    """
    This is the base class for all views that set up cookies if corresponding module was turned ON
    """

    def get_cookie_app(self):
        auth_ep = AuthorizationsEntryPoint()
        try:
            return auth_ep.module("cookie")
        except EntityNotFoundException:
            return None

    def set_cookie(self, request, response, refresh=False):
        """
        Sets the cookie

        :param request: the HTTP request
        :param response:  the HTTP response
        :param refresh: True to refresh the cookie in the database, False otherwise
        :return: nothing
        """
        auth_app = self.get_cookie_app()
        if hasattr(request, "user") and isinstance(request.user, User) and hasattr(auth_app, "set_cookie") and \
                not request.user.is_superuser and \
                (not hasattr(request, 'no_cookie') or not request.no_cookie):
            auth_app.set_cookie(request, response, refresh)
        else:
            response.delete_cookie(settings.COOKIE_NAME, settings.COOKIE_FEATURES)

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Sets the cookie when cookie authorization module was enabled and disables the cookie when the module is
        disabled

        :param request: The HTTP request
        :param response: The HTTP response
        :param args: request path arguments
        :param kwargs: request path keyword arguments
        :return: the updated version of the response
        """
        # noinspection PyUnresolvedReferences
        response = super().finalize_response(request, response, *args, **kwargs)
        self.set_cookie(request, response)
        return response
