from datetime import timedelta
from django.views.generic.base import RedirectView
from rest_framework import status

from ..entry_points.authorizations import AuthorizationsEntryPoint
from ..entity.field_managers.entity_password_manager import EntityPasswordManager


class AuthorizationView(RedirectView):
    """
    Redirection to the external authorization source
    """

    MAX_SESSION_SYMBOLS = 32
    SESSION_ID_ALPHABET = EntityPasswordManager.ALL_SYMBOLS

    request = None
    cookie_lifetime = None
    DEFAULT_COOKIE_LIFETIME = timedelta(minutes=10)

    def get(self, request, *args, **kwargs):
        session_id = EntityPasswordManager.generate_password(self.SESSION_ID_ALPHABET, self.MAX_SESSION_SYMBOLS)
        self.request = request
        self.request.session_id = session_id
        response = super().get(request, *args, **kwargs)
        if response.status_code != status.HTTP_410_GONE:
            response.set_cookie(kwargs['module_alias'], session_id, self.cookie_lifetime)
        return response

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL redirect to. Keyword arguments from the URL pattern
        match generating the redirect request are provided as kwargs to this
        method.
        """
        entry_point = AuthorizationsEntryPoint()
        module = entry_point.module(kwargs['module_alias'])
        self.cookie_lifetime = module.user_settings.get('expiry_term', self.DEFAULT_COOKIE_LIFETIME)
        return module.process_auxiliary_request(self.request)
