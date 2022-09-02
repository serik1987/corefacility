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

    def filter_queryset(self, map_set):
        """
        Applies additional filtration to the map set
        :param map_set: the map set before filtration
        :return: the map set after filtration
        """
        map_set = super().filter_queryset(map_set)
        map_set.project = self.request.project
        return map_set
