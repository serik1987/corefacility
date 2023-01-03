from rest_framework import serializers
from core.serializers import ModuleSettingsSerializer
from .. import App


class CookieSettingsSerializer(ModuleSettingsSerializer):
    """
    Provides serialization for the cookie settings
    """
    cookie_lifetime = serializers.DurationField(
        source="user_settings.cookie_lifetime",
        default=App.DEFAULT_COOKIE_LIFETIME,
        help_text="An amount of time after which the cookie is treated to be expired"
    )
