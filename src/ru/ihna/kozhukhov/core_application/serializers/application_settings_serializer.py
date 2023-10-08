from rest_framework import serializers

from .. import App as CoreApp
from .module_settings_serializer import ModuleSettingsSerializer


class ApplicationSettingsSerializer(ModuleSettingsSerializer):
    """
    Base serializer for all applications. Such serializers have 'uuid' and 'name' read-only fields and
    'is_enabled' and 'permissions' read-and-write fields.
    """

    permissions = serializers.CharField(
        source="user_settings.permissions",
        default=CoreApp.DEFAULT_APP_PERMISSION,
        help_text="Common permission level for the application"
    )
