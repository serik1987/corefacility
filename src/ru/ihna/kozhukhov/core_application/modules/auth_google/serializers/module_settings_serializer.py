from rest_framework import serializers

from ..serializers import ModuleSettingsSerializer as BaseSettingsSerializer


class ModuleSettingsSerializer(BaseSettingsSerializer):
    """
    Serializes, deserializes and validates the module settings.
    """

    client_id = serializers.CharField(
        help_text="Client ID",
        default=None,
        source="user_settings.client_id"
    )

    client_secret = serializers.CharField(
        help_text="Client Secret",
        default=None,
        source="user_settings.client_secret"
    )
