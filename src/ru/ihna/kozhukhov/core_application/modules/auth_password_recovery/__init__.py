from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.signing import Signer, BadSignature
from rest_framework.exceptions import ValidationError
from ...entity.providers.posix_providers.user_provider import UserProvider
from ...entry_points.authorizations import AuthorizationModule
from ...entity.entity_sets.user_set import UserSet
from ...exceptions.entity_exceptions import EntityNotFoundException


class PasswordRecoveryAuthorization(AuthorizationModule):
    """
    The password recovery process implies that the user receives the link with his temporary credentials
    by E-mail and then use these credentials for temporary authorization

    This requires specific authorization method through temporary rather then permanent credentials.
    We called this method as 'password recovery authorization'.

    The credentials are temporal because:
    - they are not valid for more than a week
    - they will be destroyed after the user have been authorized
    """

    DEFAULT_PASSWORD_RECOVERY_LIFETIME = timedelta(days=7)

    @property
    def app_class(self):
        """
        Returns the application class
        """
        return "ru.ihna.kozhukhov.core_application.modules.auth_password_recovery.PasswordRecoveryAuthorization"

    def get_alias(self):
        """
        Some method alias

        :return: some method alias
        """
        return "password_recovery"

    def get_name(self):
        """
        Some method name

        :return: some method name
        """
        _("Password recovery function")
        return "Password recovery function"

    def get_html_code(self):
        """
        All HTML code for this method is provided in 'core' module, no other functionality is required

        :return: None
        """
        return None

    def is_enabled_by_default(self):
        """
        By default, this method is disabled because it could be rather dangerous

        :return: False
        """
        return False

    def try_ui_authorization(self, request, view):
        """
        Provides the authorization process
        :param request: the request received from the client
        :param view: the view that invoked this method
        :return:
        """
        if not 'activation_code' in request.GET:
            return None
        try:
            activation_code = request.GET['activation_code']
            signer = Signer()
            activation_info = signer.unsign_object(activation_code)
        except BadSignature:
            return None
        try:
            user_set = UserSet()
            user_set.is_support = False
            user_set.is_locked = False
            user = user_set.get(activation_info['user_id'])
            if hasattr(request, "corefacility_log"):
                user.log = request.corefacility_log
                user.log.user = user
            user_activation_code = activation_info['user_activation_code']
        except EntityNotFoundException:
            return None
        if user.activation_code_expiry_date.is_expired():
            return None
        if not user.activation_code_hash.check(user_activation_code):
            return None
        request.no_cookie = True
        request.password = user.generate_password()
        user.activation_code_hash.clear()
        user.update()
        provider = UserProvider()
        provider.set_password(user, request.password)
        return user

    def try_api_authorization(self, request):
        pass

    def process_auxiliary_request(self, request):
        pass

    def get_password_recovery_lifetime(self):
        """
        Returns max. amount of time during which the activation link is still valid
        """
        return self.user_settings.get('password_recovery_lifetime', self.DEFAULT_PASSWORD_RECOVERY_LIFETIME)

    def get_serializer_class(self):
        """
        Defines the serializer class. The serializer class is used to represent module settings in JSON format
        :return: instance of rest_framework.serializers.Serializer class
        """
        from .serializer import PasswordRecoverySerializer
        return PasswordRecoverySerializer

    def get_pseudomodule_identity(self):
        """
        If the module is pseudo-module, the function returns some short string that is required for the frontend to
        identify the pseudo-module.
        :return: a string containing the pseudo-module identity
        """
        return 'password_recovery'

    def is_enableable(self, new_value):
        """
        Checks whether the module can be enabled or disabled
        :param new_value: new module value to set
        :return: nothing. If the operation is impossible, raise exception
        """
        if new_value:
            if not settings.EMAIL_SUPPORT:
                raise ValidationError({'is_enabled': _("The module can't be enabled without email support")})
