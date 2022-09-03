from rest_framework import serializers

from imaging.serializers import MapRelatedSerializer
from roi.entity import Pinwheel


class PinwheelSerializer(MapRelatedSerializer):
    """
    Transforms the Pinwheel entity to Python primitives and vice versa.
    Also, performs data validation
    """

    entity_class = Pinwheel

    id = serializers.ReadOnlyField(help_text="pinwheel ID")
    x = serializers.IntegerField(min_value=0, help_text="pinwheel abscissa (x) in pixels")
    y = serializers.IntegerField(min_value=0, help_text="pinwheel ordinate (y) in pixels")
