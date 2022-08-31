from django.utils.translation import gettext
from rest_framework import serializers

from .entity_serializer import EntitySerializer


class ModuleSerializer(EntitySerializer):
    """
    Transforms a module to its primitive representation
    """

    uuid = serializers.SerializerMethodField(help_text="Unique module ID")
    alias = serializers.ReadOnlyField(help_text="Module string identifier (alias or slug)")
    name = serializers.SerializerMethodField(help_text="Human-readable module name")

    def get_uuid(self, module):
        """
        Provides string representation of the module UUID
        :param module: modules which UUID shall be revealed
        :return: string representation of the UUID
        """
        return str(module.uuid)

    def get_name(self, module):
        """
        Provides localized representation of the module name
        :param module: module which name shall be revealed
        :return: Module name translated into current language
        """
        return gettext(module.name)
