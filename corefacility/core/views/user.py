import urllib

from django.core.signing import Signer
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from core import App
from core.utils import mail
from core.api_exceptions import MailAddressUndefinedException, MailFailedException
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
        from core.os.command_maker import CommandMaker
        with CorefacilityTransaction():
            user = self.get_object()
            symbol_alphabet = EntityPasswordManager.SMALL_LATIN_LETTERS + EntityPasswordManager.DIGITS + \
                EntityPasswordManager.BIG_LATIN_LETTERS
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

    @action(detail=True, methods=['post'], url_path="activation-mail")
    def activation_mail(self, request, *args, **kwargs):
        app = App()
        user = self.get_object()
        if not user.email or user.email == "":
            raise MailAddressUndefinedException()
        alphabet = EntityPasswordManager.ALL_SYMBOLS
        code_size = app.get_max_activation_code_symbols()
        user_activation_code = user.activation_code_hash.generate(alphabet, code_size)
        user.activation_code_expiry_date.set(app.get_activation_code_lifetime())
        user.update()
        signer = Signer()
        activation_code = signer.sign_object({
            "user_id": user.id,
            "user_activation_code": user_activation_code
        })
        query_params = urllib.parse.urlencode({"activation_code": activation_code})
        activation_url = "%s://%s/?%s" % (request.scheme, request.get_host(), query_params)
        try:
            mail(
                template_prefix="core/activation_mail",
                context_data={
                    "surname": user.surname,
                    "name": user.name,
                    "host": request.get_host(),
                    "activation_url": activation_url
                },
                subject=_("Account activation"),
                recipient=user.email
            )
        except OSError as error:
            raise MailFailedException(error)
        return Response({})
