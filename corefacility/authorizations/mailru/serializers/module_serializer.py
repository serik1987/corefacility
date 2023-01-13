from datetime import timedelta
from rest_framework import serializers

from core.serializers import ModuleSettingsSerializer


class ModuleSerializer(ModuleSettingsSerializer):
    """
    Provides serialization, de-serialization and validation of the module settings
    """

    client_id = serializers.CharField(
        source="user_settings.client_id",
        default=None,
        help_text="The client ID will be given upon application registration via Mail.Ru"
    )

    client_secret = serializers.CharField(
        source="user_settings.client_secret",
        default=None,
        help_text="The client secret will be given upon application registration via Mail.Ru"
    )

    expiry_term = serializers.DurationField(
        source="user_settings.expiry_term",
        default=timedelta(minutes=10),
        help_text="Expiry term of the pairing token"
    )
