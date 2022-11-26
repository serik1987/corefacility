from datetime import timedelta
from rest_framework import serializers

from core import App
from core.entity.entry_points.entry_point_set import EntryPointSet

from .module_settings_serializer import ModuleSettingsSerializer


class CoreSettingsSerializer(ModuleSettingsSerializer):
    """
    Serializes, deserializes and validates the 'core' module settings
    """

    is_enabled = serializers.ReadOnlyField(help_text="Is module enabled? (Always True)")

    max_password_symbols = serializers.IntegerField(
        source="user_settings.max_password_symbols",
        default=App.DEFAULT_MAX_PASSWORD_SYMBOLS,
        min_value=6,
        help_text="Maximum number of password symbols in the serializer"
    )

    auth_token_lifetime = serializers.DurationField(
        source="user_settings.auth_token_lifetime",
        default=App.DEFAULT_AUTH_TOKEN_LIFETIME,
        min_value=timedelta(minutes=5),
        help_text="Lifetime for the authorization token"
    )

    is_user_can_change_password = serializers.BooleanField(
        source="user_settings.is_user_can_change_password",
        default=App.DEFAULT_USER_CAN_CHANGE_HIS_PASSWORD,
        help_text="True if the user can change his password, False if only administrator can do this"
    )
