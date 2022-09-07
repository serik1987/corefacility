from django.utils.translation import gettext
from rest_framework import serializers

from .entity_serializer import EntitySerializer


class ModuleSettingsSerializer(EntitySerializer):
    """
    This is the base class that allows serialization or deserialization of the module settings
    """

    uuid = serializers.UUIDField(read_only=True, help_text="Module UUID")
    name = serializers.SerializerMethodField(help_text="Human-readable module name")
    is_enabled = serializers.BooleanField(required=True, help_text="True if the module is enabled, False otherwise")

    def get_name(self, module):
        """
        Returns the module name
        :param module: module which name shall be returned
        :return: human-readable name of that module
        """
        return gettext(module.name)
