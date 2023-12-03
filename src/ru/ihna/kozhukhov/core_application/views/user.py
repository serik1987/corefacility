import urllib

from django.core.signing import Signer
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .. import App
from ..modules.auth_password_recovery import PasswordRecoveryAuthorization
from ..utils import mail
from ..exceptions.api_exceptions import MailAddressUndefinedException, MailFailedException, PasswordRecoverySwitchedOff
from ru.ihna.kozhukhov.core_application.entity.entity_sets.user_set import UserSet
from ..entity.field_managers.entity_password_manager import EntityPasswordManager
from ru.ihna.kozhukhov.core_application.generic_views import EntityViewSet, AvatarMixin
from ru.ihna.kozhukhov.core_application.serializers import UserListSerializer, UserDetailSerializer
from ru.ihna.kozhukhov.core_application.permissions import AdminOnlyPermission
from .password_reset_mixin import PasswordResetMixin


class UserViewSet(AvatarMixin, PasswordResetMixin, EntityViewSet):
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

    def filter_queryset(self, user_set):
        """
        Adjusts filter parameters of the UserSet object

        :param user_set: the UserSet object before the parameters are adjusted
        :return: the UserSet object after all parameters are adjusted
        """
        user_set = super().filter_queryset(user_set)
        user_set.is_support = False
        return user_set

    def destroy(self, request, *args, **kwargs):
        """
        Removes the user from the database.

        :param request: the HTTP request received
        :param args: always ()
        :param kwargs: user ID or alias
        """
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
        return super().password_reset(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path="activation-mail")
    def activation_mail(self, request, *args, **kwargs):
        PasswordRecoveryAuthorization.reset()
        app = App()
        auth_app = PasswordRecoveryAuthorization()
        if not auth_app.is_enabled:
            raise PasswordRecoverySwitchedOff()
        user = self.get_object()
        if not user.email or user.email == "":
            raise MailAddressUndefinedException()
        alphabet = EntityPasswordManager.ALL_SYMBOLS
        code_size = app.get_max_activation_code_symbols()
        user_activation_code = user.activation_code_hash.generate(alphabet, code_size)
        user.activation_code_expiry_date.set(auth_app.get_password_recovery_lifetime())
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
