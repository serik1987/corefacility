import numpy

from core.generic_views import EntityViewSet
from imaging.generics import FunctionalMapMixin
from imaging.decorators import map_processing
from roi import App
from roi.entity import PinwheelSet
from roi.serializers import PinwheelSerializer
from roi.api_exceptions import *


class PinwheelViewSet(FunctionalMapMixin, EntityViewSet):
    """
    Dealing with pinwheels
    """
    @staticmethod
    def sqr(x):
        """
        Calculates the square of x
        :param x: a value which square shall be calculated
        :return: result of the square calculation
        """
        return x*x

    application = App()
    data_gathering_way = 'processing'
    entity_set_class = PinwheelSet
    list_serializer_class = PinwheelSerializer
    detail_serializer_class = PinwheelSerializer

    @map_processing(target_alias_suffix="distance", detail=False, url_path="distance_map", url_name="distance-map")
    def calculate_distance_map(self, source_data, pinwheel_set):
        """
        Calculate the distance map using a set of manually defined pinwheel centers
        :param source_data: useless
        :param pinwheel_set: an instance of the PinwheelSet object
        :return: 2D map of distances to the nearest pinwheel center
        """
        map_width, map_height = self.request.functional_map.width, self.request.functional_map.height
        if map_width is None or map_height is None:
            raise BadDimensionsException()
        res_y, res_x = source_data.shape
        x_1d = numpy.arange(res_x, dtype=numpy.float)
        y_1d = numpy.arange(res_y, dtype=numpy.float)
        x, y = numpy.meshgrid(x_1d, y_1d)
        target_map = None
        for pinwheel in pinwheel_set:
            distance_map = self.sqr(x - pinwheel.x) + self.sqr(y - pinwheel.y)
            if target_map is None:
                target_map = distance_map
            else:
                target_map = numpy.minimum(target_map, distance_map)
        if target_map is None:
            raise NoPinwheelException()
        return numpy.sqrt(target_map)
