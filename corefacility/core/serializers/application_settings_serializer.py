from rest_framework import serializers

from core import App as CoreApp
from core.models.enums import LevelType
from core.entity.access_level import AccessLevelSet
from core.entity.entity_exceptions import EntityNotFoundException
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

    def validate_permissions(self, value):
        """
        Provides extra validation for the 'permissions' field
        :param value: value of this field before extra validation
        :return: value of this field after extra validation
        """
        level_set = AccessLevelSet()
        level_set.type = LevelType.app_level
        try:
            level_set.get(value)
        except EntityNotFoundException:
            raise serializers.ValidationError("To frontend developers: value of this field must be mentioned in the "
                                              "access level list as application permission and hence not valid")
        return value
