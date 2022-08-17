from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from core import App
from core.os.user import PosixUser, OperatingSystemUserNotFoundException
from core.transaction import CorefacilityTransaction
from ..entity.user import UserSet
from ..entity.entity_providers.posix_providers.user_provider import UserProvider as PosixProvider
from ..entity.entity_fields.field_managers.entity_password_manager import EntityPasswordManager
from ..generic_views import EntityViewSet, AvatarMixin
from ..serializers import UserListSerializer, UserDetailSerializer
from ..permissions import AdminOnlyPermission


class UserViewSet(AvatarMixin, EntityViewSet):
    """
    Deals with list of users.
    """

    permission_classes = [AdminOnlyPermission]

    entity_set_class = UserSet

    list_serializer_class = UserListSerializer

    detail_serializer_class = UserDetailSerializer

    list_filters = {
        "name": EntityViewSet.standard_filter_function("q", str),
    }

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.id == request.user.id:
            raise PermissionDenied(detail=_("You can't delete yourself."))
        if "force" in request.query_params:
            user.force_delete()
        else:
            user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path="password-reset")
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
            symbol_alphabet = EntityPasswordManager.SMALL_LATIN_LETTERS + EntityPasswordManager.DIGITS
            max_symbols = App().get_max_password_symbols()
            new_password = user.password_hash.generate(symbol_alphabet, max_symbols)
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
