from rest_framework import serializers

from imaging.serializers.map_related_serializer import MapRelatedSerializer
from roi.entity import RectangularRoi


class RectangularRoiSerializer(MapRelatedSerializer):
    """
    Provides serialization, deserialization of the rectangular ROI and validation of user's input data
    connected to the rectangular ROI
    """

    entity_class = RectangularRoi

    id = serializers.ReadOnlyField(help_text="ID of the rectangular ROI")
    left = serializers.IntegerField(min_value=0, help_text="Position of the left border")
    right = serializers.IntegerField(min_value=0, help_text="Position of the right border")
    top = serializers.IntegerField(min_value=0, help_text="Position of the top border")
    bottom = serializers.IntegerField(min_value=0, help_text="Position of the bottom border")
