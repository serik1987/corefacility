from uuid import UUID
from rest_framework.response import Response

from core.entity.corefacility_module import CorefacilityModuleSet
from core.generic_views import EntityViewSet
from core.permissions import AdminOnlyPermission


class ModuleSettingsViewSet(EntityViewSet):
    """
    Module settings, install and/or uninstall
    """

    permission_classes = [AdminOnlyPermission]
    entity_set_class = CorefacilityModuleSet

    def retrieve(self, request, *args, **kwargs):
        module = self.get_object()
        module_serializer = module.get_serializer_class()(module)
        return Response(module_serializer.data)

    def get_object(self):
        """
        Returns current object for detail path usage or raises an exception for list path usage.
        Also, the function checks object permissions.
        :return: an instance of the core.entity.corefacility_module.CorefacilityModule class
        """
        entity_set = self.filter_queryset(self.get_queryset())
        lookup_value = UUID(self.kwargs['lookup'])
        module = self.get_entity_or_404(entity_set, lookup_value)
        return module
