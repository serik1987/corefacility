from rest_framework.exceptions import MethodNotAllowed

from core.generic_views import EntityRetrieveUpdateView
from core.serializers import ProfileSerializer
from core.permissions import NoSupportPermission

from .password_reset_mixin import PasswordResetMixin


class ProfileView(PasswordResetMixin, EntityRetrieveUpdateView):
    """
    Working with profile information
    """

    action = 'default'

    detail_serializer_class = ProfileSerializer
    permission_classes = [NoSupportPermission]

    def get_object(self):
        """
        Returns a user which profile is going to be changed.

        :return: a user which profile is going to be changed
        """
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
        Dispacthes the POST request
        :param request: the request to be dispatched
        :param args: parameters extracted from the request path
        :param kwargs: keyword parameters extracted from the request path
        :return: the response to be sent to the user
        """
        if self.action == 'password_reset':
            return self.password_reset(request, *args, **kwargs)
        raise MethodNotAllowed('POST')
