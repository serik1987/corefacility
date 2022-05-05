from django.core.signing import BadSignature
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.entity_exceptions import EntityNotFoundException


class CoreAuthentication(BaseAuthentication):
    """
    Provides the standard global authentication for all requests.
    """

    AUTHORIZATION_HEADER_START = "Token "

    def authenticate(self, request):
        """
        Authenticates the request. Throws error 401 if authentication is failed.

        :param request: the request to be authenticated
        :return: A tuple (user, token) if authentication is successful, None otherwise.
        """
        if "Authorization" in request.headers:
            authorization_header = request.headers["Authorization"]
            if authorization_header.startswith(self.AUTHORIZATION_HEADER_START):
                try:
                    token = authorization_header.split(self.AUTHORIZATION_HEADER_START, 1)[1]
                    user = AuthorizationModule.apply_token(token)
                    user.is_authenticated = True
                    if hasattr(request, "corefacility_log"):
                        request.corefacility_log.user = user
                    return user, token
                except (BadSignature, EntityNotFoundException):
                    raise AuthenticationFailed()

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return "Token"
