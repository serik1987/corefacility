from django.utils.translation import gettext as _
from rest_framework import serializers

from core.serializers import EntitySerializer
from imaging.entity import Map


def non_zero_validator(value):
    if value == 0.0:
        raise serializers.ValidationError(_("This value shall not be zero"))
    return value


class MapSerializer(EntitySerializer):
    """
    Provides transformation of the functional map to its string representation and vice verse.
    Also, validates the data entered by the user
    """

    entity_class = Map

    id = serializers.ReadOnlyField(help_text="Map ID")
    alias = serializers.SlugField(max_length=50, required=True, allow_null=False, help_text="Map string ID")
    data = serializers.ReadOnlyField(help_text="Map data URL", source="data.url")
    type = serializers.ChoiceField(("ori", "dir"), required=True, allow_null=False,
                                   help_text="'ori' for orientation maps, 'dir' for directional maps")
    resolution_x = serializers.ReadOnlyField(help_text="Map width in pixels")
    resolution_y = serializers.ReadOnlyField(help_text="map height in pixels")
    width = serializers.FloatField(min_value=0, required=False, allow_null=True, validators=[non_zero_validator],
                                   help_text="Map width in um")
    height = serializers.FloatField(min_value=0, required=False, allow_null=True, validators=[non_zero_validator],
                                    help_text="Map height in um")

    def create(self, data):
        """
        Creates new functional map
        :param data: the data sent by the Web browser
        :return: the Map entity that shall be created
        """
        data['project'] = self.context['request'].project
        return super().create(data)
