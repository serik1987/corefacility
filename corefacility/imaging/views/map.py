from core.generic_views import EntityViewSet
from imaging import App
from imaging.entity import MapSet
from imaging.serializers import MapSerializer


class MapViewSet(EntityViewSet):
    """
    Working with functional maps
    """

    application = App()
    data_gathering_way = "uploading"
    entity_set_class = MapSet
    list_serializer_class = MapSerializer
    detail_serializer_class = MapSerializer
