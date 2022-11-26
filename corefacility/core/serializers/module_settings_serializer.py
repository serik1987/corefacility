from django.utils.translation import gettext
from rest_framework import serializers

from .entity_serializer import EntitySerializer


class ModuleSettingsSerializer(EntitySerializer):
    """
    This is the base class that allows serialization or deserialization of the module settings
    """

    uuid = serializers.UUIDField(read_only=True, help_text="Module UUID")
    alias = serializers.ReadOnlyField(help_text="Module alias")
    name = serializers.SerializerMethodField(help_text="Human-readable module name")
    is_enabled = serializers.BooleanField(required=True, help_text="True if the module is enabled, False otherwise")
    node_number = serializers.ReadOnlyField(help_text="Number of entry points attached to the module")

    def get_name(self, module):
        """
        Returns the module name
        :param module: module which name shall be returned
        :return: human-readable name of that module
        """
        return gettext(module.name)

    def update(self, module, validated_data):
        """
        Sets the module settings
        :param module: the corefacility module which settings must be adjusted
        :param validated_data: input data after they have been validated
        :return: the updated entity
        """
        if 'user_settings' in validated_data:
            for key, value, in validated_data['user_settings'].items():
                module.user_settings.set(key, value)
            del validated_data['user_settings']
        return super().update(module, validated_data)
