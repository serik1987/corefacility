from rest_framework import serializers

from ...serializers import ModuleSettingsSerializer


class StandardAuthorizationSerializer(ModuleSettingsSerializer):
    """
    Provides serialization, deserialization and validation for the settings of the standard authorization module.
    """
    max_failed_authorization_number = serializers.IntegerField(
        source="user_settings.max_failed_authorization_number",
        default=50,
        min_value=5,
        help_text="Maximum number of unsuccessful authorizations after which throttling will be applied"
    )
