from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from core.generic_views import SetCookieMixin
from core.permissions import AdminOrSelfPermission
from core.entity.user import UserSet
from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.entry_points.authorizations import AuthorizationsEntryPoint


class AuthorizationMethodSetupView(SetCookieMixin, APIView):
    """
    Working with authorization properties for a particular user
    """

    permission_classes = [AdminOrSelfPermission]

    def get(self, request, *args, **kwargs):
        """
        Retrieves the authorization properties
        :param request: the HTTP request received from the client
        :param args: request arguments
        :param kwargs: request keyword arguments
        :return: the HTTP response to be sent to the user
        """
        user = self._get_user()
        module = self._get_authorization_module()
        return Response(module.get_user_settings(user))

    def post(self, request, *args, **kwargs):
        """
        Retrieves the authorization properties
        :param request: the HTTP request received from the client
        :param args: request arguments
        :param kwargs: request keyword arguments
        :return: the HTTP response to be sent to the user
        """
        user = self._get_user()
        module = self._get_authorization_module()
        serializer_class = module.get_user_settings_serializer_class(user)
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        module.set_user_settings(user, serializer.validated_data)
        return Response(serializer.validated_data)

    def _get_user(self):
        """
        Returns the user mentioned in the request path string
        """
        try:
            return UserSet().get(self.kwargs['user_id'])
        except EntityNotFoundException:
            raise NotFound()

    def _get_authorization_module(self):
        """
        Returns the authorization module mentioned in the request path string
        """
        try:
            return AuthorizationsEntryPoint().module(self.kwargs['module_alias'], True)
        except EntityNotFoundException:
            raise NotFound()
