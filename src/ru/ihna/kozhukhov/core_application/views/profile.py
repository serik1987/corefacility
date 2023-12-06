from rest_framework.exceptions import MethodNotAllowed, PermissionDenied

from .. import App
from ..generic_views import EntityRetrieveUpdateView
from ..serializers import ProfileSerializer
from ..permissions import NoSupportPermission

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
        if hasattr(self.request, 'corefacility_log'):
            self.request.user.log = self.request.corefacility_log
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

    def password_reset(self, request, *args, **kwargs):
        """
        Resets the user password
        :param request: REST framework request
        :param args: position arguments
        :param kwargs: dictionary arguments
        :return: REST framework response
        """
        app = App()
        if app.user_can_change_password():
            return super().password_reset(request, *args, **kwargs)
        else:
            raise PermissionDenied("Current control panel settings don't allow the user to change his password.")
