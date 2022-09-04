from django.utils.translation import gettext as _
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

    def validate(self, data):
        """
        Provides additional data validation of the input data containing in the request body
        :param data: input data before additional validation
        :return: input data after additional validation
        """
        left_border = data['left'] if 'left' in data else self.instance.left
        right_border = data['right'] if 'right' in data else self.instance.right
        top_border = data['top'] if 'top' in data else self.instance.top
        bottom_border = data['bottom'] if 'bottom' in data else self.instance.bottom
        if left_border >= right_border or top_border >= bottom_border:
            raise serializers.ValidationError(_("Incorrect combination of ROI border values"))
        return data
