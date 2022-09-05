from functools import wraps
import numpy
from django.http import HttpResponseRedirect
from rest_framework.decorators import action

from core.entity.entity_exceptions import EntityNotFoundException
from imaging.entity import MapSet
from imaging.api_exceptions import TargetMapAliasException


def map_processing(target_alias_suffix="proc", detail=True, url_path="proc", url_name="proc"):
    """
    Transforms a single function to so called 'map_procesor': a function that loads the data from the hard disk,
    process it using such a single function and saves the processing results to the hard disk drive's file as well as
    to the database

    Such function is suitable for writing map processing algorithms
    :param target_alias_suffix: any map processing will create the target functional map which alias will be produced
        from the alias of the source functional map by attaching the 'target_alias_suffix'
    :param detail: True if you need to use single map-related entity to process the map - its ID shall be expliticly
    written to the resource path, False if you need to use the whole entity list, in this case whole resource path
    shall be omitted
    :param url_path: url segment that you need to attach to the resource list or detail URL to launch the processing
    :param url_name: suffix to build the URL name (to be used for reverse mapping). Such a suffix will be attached
        to the basename
    :return:
    """

    def decorator(inner_func):
        @action(methods=["POST"], detail=detail, url_path=url_path, url_name=url_name)
        @wraps(inner_func)
        def outer_func(self, request, *args, **kwargs):
            if detail:
                map_processing_detail = self.get_object()
            else:
                map_processing_detail = self.filter_queryset(self.get_queryset())
            target_alias = "%s_%s" % (request.functional_map.alias, target_alias_suffix)
            try:
                MapSet().get(target_alias)
                raise TargetMapAliasException(target_alias)
            except EntityNotFoundException:
                pass
            source_data = self.load_map_data()
            target_data = inner_func(self, source_data, map_processing_detail)
            if not isinstance(target_data, numpy.ndarray):
                raise ValueError("The function decorated by @map_processing decorator must return the NUMPY array")
            map_url = self.save_map_data(target_alias, target_data)
            return HttpResponseRedirect(redirect_to=map_url)
        return outer_func
    return decorator
