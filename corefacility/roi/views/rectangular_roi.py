from django.http import HttpResponseRedirect
from rest_framework.decorators import action

from core.entity.entity_exceptions import EntityNotFoundException
from core.generic_views import EntityViewSet
from imaging.entity import MapSet
from imaging.generics import FunctionalMapMixin
from imaging.decorators import map_processing
from imaging.api_exceptions import TargetMapAliasException
from roi import App
from roi.entity import RectangularRoiSet
from roi.serializers import RectangularRoiSerializer


class RectangularRoiViewSet(FunctionalMapMixin, EntityViewSet):
    """
    Dealing with rectangular ROIs
    """

    application = App()
    """ Security option: application related to this view """

    data_gathering_way = 'processing'
    """ Security option: the purpose of this features: 'uploading' for data uploading from external source,
        'processing' for data processing """

    entity_set_class = RectangularRoiSet
    """ The entity set class related to this view """

    list_serializer_class = RectangularRoiSerializer
    """ The view will use its own serializer """

    detail_serializer_class = RectangularRoiSerializer
    """ The view will use its own serializer """

    pagination_class = None
    """ No pagination since it hardens the development of graphical editor. """

    @map_processing(target_alias_suffix="cut", detail=True, url_path="cut_map", url_name="apply")
    def apply_roi(self, source_data, roi):
        """
        Cuts map using the ROI and returns smaller one
        :param source_data: numpy 2D array that reflect source map before cutting
        :param roi: an instance of roi.entity.Roi entity that will be used to cut the map
        :return: numpy 2D array that reflects target map after cutting
        """
        return source_data[roi.top:roi.bottom, roi.left:roi.right]
