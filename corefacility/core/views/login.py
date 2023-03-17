from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.entity.entry_points import AuthorizationsEntryPoint
from core.generic_views import SetCookieMixin
from core.serializers import ProfileSerializer


class LoginView(SetCookieMixin, APIView):
    """
    User login.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """
        Provides the API login

        :param request: REST framework request
        :param args: arguments
        :param kwargs: keyword arguments
        :return: REST framework response
        """
        auth_point = AuthorizationsEntryPoint()
        user = None
        for auth_module in auth_point.modules():
            user = auth_module.try_api_authorization(request)
            if user is not None and user.is_locked:
                user = None
            if user is not None:
                break
        if user is None:
            raise NotAuthenticated(_("Incorrect credentials."), code="authorization_failed")
        token = auth_module.issue_token(user)
        user_serializer = ProfileSerializer(user)
        if hasattr(request, "corefacility_log"):
            request.corefacility_log.response_body = "***"
        request.user = user  # Otherwise cookies will not work
        return Response({
            "token": token,
            "user": user_serializer.data,
        })
