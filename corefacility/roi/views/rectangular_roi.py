from core.generic_views import EntityViewSet
from imaging.generics import FunctionalMapMixin
from roi import App
from roi.entity import RectangularRoiSet
from roi.serializers import RectangularRoiSerializer


class RectangularRoiViewSet(FunctionalMapMixin, EntityViewSet):
    """
    Dealing with rectangular ROIs
    """

    application = App()
    data_gathering_way = 'processing'
    entity_set_class = RectangularRoiSet
    list_serializer_class = RectangularRoiSerializer
    detail_serializer_class = RectangularRoiSerializer
