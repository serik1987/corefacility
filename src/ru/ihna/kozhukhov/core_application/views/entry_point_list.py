from rest_framework.exceptions import NotFound

from ..entity.entity_sets.entry_point_set import EntryPointSet
from ..entity.corefacility_module import CorefacilityModuleSet
from ..exceptions.entity_exceptions import EntityNotFoundException
from ..generic_views import EntityListView
from ..permissions import AdminOnlyPermission
from ..serializers import EntryPointSerializer


class EntryPointListView(EntityListView):
    """
    Provides list of all entry points connected to a given module
    """

    permission_classes = [AdminOnlyPermission]
    entity_set_class = EntryPointSet
    list_serializer_class = EntryPointSerializer
    detail_serializer_class = None
    pagination_class = None

    def filter_queryset(self, entry_point_set):
        """
        Provides additional filtration of the entry point set
        :param entry_point_set: entry point set before the additional filtration
        :return: entry point set after the additional filtration
        """
        try:
            module = CorefacilityModuleSet().get(self.kwargs['uuid'])
        except EntityNotFoundException:
            raise NotFound()
        entry_point_set.parent_module = module
        return entry_point_set
