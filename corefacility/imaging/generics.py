from core.generic_views import EntityViewMixin


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
        entity_set = super().filter_queryset(entity_set)
        try:
            entity_set.map_id = int(self.kwargs['map_lookup'])
        except ValueError:
            entity_set.map_alias = self.kwargs['map_lookup']
        entity_set.project_id = self.request.project.id
        return entity_set
