from django.utils.translation import gettext
from rest_framework import serializers

from core.entity.entry_points.entry_point_set import EntryPointSet

from .entity_serializer import EntitySerializer


class ModuleSerializer(EntitySerializer):
    """
    Transforms a module to its primitive representation
    """

    uuid = serializers.SerializerMethodField(help_text="Unique module ID")
    alias = serializers.ReadOnlyField(help_text="Module string identifier (alias or slug)")
    name = serializers.SerializerMethodField(help_text="Human-readable module name")
    node_number = serializers.ReadOnlyField(help_text="Number of entry points that the module has")
    pseudomodule_identity = serializers.SerializerMethodField(
        help_text="A short string that will help the corefacility-core frontend to select proper client model and "
                  "form for the module")

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

    def get_pseudomodule_identity(self, module):
        """
        Provides a pseudo-module identity
        :param module: a module which identity must be provided
        :return: the pseudo-module identity
        """
        return module.get_pseudomodule_identity()
