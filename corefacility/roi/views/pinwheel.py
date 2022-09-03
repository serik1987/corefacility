from core.generic_views import EntityViewSet
from imaging.generics import FunctionalMapMixin
from roi import App
from roi.entity import PinwheelSet
from roi.serializers import PinwheelSerializer


class PinwheelViewSet(FunctionalMapMixin, EntityViewSet):
    """
    Dealing with pinwheels
    """

    application = App()
    data_gathering_way = 'processing'
    entity_set_class = PinwheelSet
    list_serializer_class = PinwheelSerializer
    detail_serializer_class = PinwheelSerializer
