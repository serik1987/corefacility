from django.db import transaction
from rest_framework.response import Response

from ..entity.providers.posix_providers.user_provider import UserProvider as PosixProvider


# noinspection PyUnresolvedReferences
class PasswordResetMixin:
    """
    Resets the password
    """

    def password_reset(self, request, *args, **kwargs):
        """
        Resets the user password
        :param request: REST framework request
        :param args: position arguments
        :param kwargs: dictionary arguments
        :return: REST framework response
        """
        with transaction.atomic():
            user = self.get_object()
            new_password = user.generate_password()
            user.update()
            provider = PosixProvider()
            provider.set_password(user, new_password)
            if hasattr(request, 'corefacility_log'):
                request.corefacility_log.response_body = "***"
        return Response({"password": new_password})
