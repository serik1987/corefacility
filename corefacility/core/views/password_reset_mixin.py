from django.conf import settings
from rest_framework.response import Response

from ..entity.entity_providers.posix_providers.user_provider import UserProvider as PosixProvider
from core.os.user import PosixUser, OperatingSystemUserNotFoundException
from core.transaction import CorefacilityTransaction


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
        with CorefacilityTransaction():
            user = self.get_object()
            new_password = user.generate_password()
            if PosixProvider().is_provider_on() and not settings.CORE_SUGGEST_ADMINISTRATION:
                try:
                    posix_user = PosixUser.find_by_login(user.unix_group)
                    posix_user.set_password(new_password)
                    if user.is_locked:
                        posix_user.lock()
                except OperatingSystemUserNotFoundException:
                    pass
            request.corefacility_log.response_body = "***"
            user.update()
        return Response({"password": new_password})
