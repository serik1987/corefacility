from django.utils.translation import gettext
from rest_framework import serializers

from .entity_serializer import EntitySerializer


class EntryPointSerializer(EntitySerializer):
    """
    Provides serialization of entry points
    """

    id = serializers.ReadOnlyField(help_text="Entry point ID")
    alias = serializers.ReadOnlyField(help_text="Short name of the entry point")
    name = serializers.SerializerMethodField(help_text="Entry point name")

    def get_name(self, entry_point):
        """
        Estimates the entry point name
        :param entry_point: entry point which name shall be estimated
        :return: entry point's name
        """
        return gettext(entry_point.name)
