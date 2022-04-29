from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.entity.entry_points import AuthorizationsEntryPoint
from core.serializers import UserListSerializer


class LoginView(APIView):
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
        print(request.version)
        auth_point = AuthorizationsEntryPoint()
        user = None
        for auth_module in auth_point.modules():
            user = auth_module.try_api_authorization(request)
            if user is not None:
                break
        if user is None:
            raise NotAuthenticated()
        token = auth_module.issue_token(user)
        user_serializer = UserListSerializer(user)
        request.corefacility_log.response_body = "***"
        return Response({
            "token": token,
            "user": user_serializer.data,
        })
