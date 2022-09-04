from django.http import HttpResponseRedirect
from rest_framework.decorators import action

from core.entity.entity_exceptions import EntityNotFoundException
from core.generic_views import EntityViewSet
from imaging.entity import MapSet
from imaging.generics import FunctionalMapMixin
from imaging.api_exceptions import TargetMapAliasException
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

    @action(methods=["POST"], detail=True, url_path="cut_map", url_name="apply")
    def apply_roi(self, request, *args, **kwargs):
        """
        Applies ROI to reveal smaller functional map
        :param request: request
        :param args: arguments
        :param kwargs: keyword arguments
        :return: nothing
        """
        entity = self.get_object()
        target_alias = "%s_cut" % request.functional_map.alias
        try:
            MapSet().get(target_alias)
            raise TargetMapAliasException(target_alias)
        except EntityNotFoundException:
            pass
        source_data = self.load_map_data()
        target_data = source_data[entity.top:entity.bottom, entity.left:entity.right]
        map_url = self.save_map_data(target_alias, target_data)
        return HttpResponseRedirect(redirect_to=map_url)
