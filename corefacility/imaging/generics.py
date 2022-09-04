from rest_framework.exceptions import NotFound

from core.generic_views import EntityViewMixin
from core.entity.entity_exceptions import EntityNotFoundException
from imaging.entity import MapSet


class FunctionalMapMixin(EntityViewMixin):
    """
    The base class for all views dealing with functional map processing
    """

    def filter_queryset(self, entity_set):
        """
        Provides additional filtration of the pinwheel set
        :param entity_set: the pinwheel set before the filtration
        :return: the pinwheel set after the filtration
        """
        map_set = MapSet()
        map_set.project = self.request.project
        try:
            map_lookup = int(self.kwargs['map_lookup'])
        except ValueError:
            map_lookup = self.kwargs['map_lookup']
        try:
            functional_map = map_set.get(map_lookup)
        except EntityNotFoundException:
            raise NotFound()
        entity_set = super().filter_queryset(entity_set)
        entity_set.map = functional_map
        return entity_set
