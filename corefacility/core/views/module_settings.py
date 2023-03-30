from uuid import UUID
from django.utils.translation import gettext
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from core.entity.corefacility_module import CorefacilityModuleSet
from core.entity.entry_points.entry_point_set import EntryPointSet
from core.entity.entity_exceptions import EntityNotFoundException
from core.generic_views import EntityViewSet
from core.pagination import CorePagination
from core.permissions import ModuleSettingsPermission
from core.serializers import ModuleSerializer


class ModuleSettingsViewSet(EntityViewSet):
    """
    Module settings, install and/or uninstall
    """

    permission_classes = [ModuleSettingsPermission]
    entity_set_class = CorefacilityModuleSet
    list_serializer_class = ModuleSerializer
    detail_serializer_class = None
    pagination_class = None

    def create(self, request, *args, **kwargs):
        raise PermissionDenied(detail="TO-DO: install module routines")

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied(detail="TO-DO: delete module routines")

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of all modules

        :param request: the request sent by the user
        :param args: request arguments
        :param kwargs: request keyword arguments
        :return: the response to be sent to the user
        """
        if "q" in request.query_params:
            if request.query_params['profile'] != 'light':
                raise PermissionDenied(detail="Module search is not available for the basic profile")
            search_term = request.query_params['q']
            module_set = self.filter_queryset(self.get_queryset())
            module_list = []
            modules_added = 0
            for module in module_set:
                if gettext(module.name).find(search_term) != -1:
                    module_list.append(ModuleSerializer(module).data)
                    modules_added += 1
                if modules_added > CorePagination.PAGE_SIZES[request.query_params['profile']]:
                    break
            return Response(module_list)
        else:
            return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves user settings for a given module
        :param request: the request received from the client
        :param args: results of the request path parsing
        :param kwargs: results of the request path parsing
        :return: the response to be sent to the client
        """
        module = self.get_object()
        module_serializer = module.get_serializer_class()(module)
        return Response(module_serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        module = self.get_object()
        serializer = module.get_serializer_class()(module, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def filter_queryset(self, module_set):
        """
        Filters the existent module set
        :param module_set: module set before the filtration process
        :return: module set after the filtration process
        """
        if "entry_point" in self.request.query_params:
            ep_lookup = self.request.query_params['entry_point']
            if ep_lookup == "" or ep_lookup == "0":
                module_set.is_root_module = True
            else:
                try:
                    ep_id = int(ep_lookup)
                    ep_set = EntryPointSet()
                    entry_point = ep_set.get(ep_id)
                    module_set.entry_point = entry_point
                except (ValueError, EntityNotFoundException):
                    raise ValidationError("incorrect entry point ID")
        if "enabled_apps_only" in self.request.query_params:
            module_set.is_enabled = True
            module_set.is_application = True
        return module_set

    def get_object(self):
        """
        Returns current object for detail path usage or raises an exception for list path usage.
        Also, the function checks object permissions.
        :return: an instance of the core.entity.corefacility_module.CorefacilityModule class
        """
        entity_set = self.filter_queryset(self.get_queryset())
        try:
            lookup_value = UUID(self.kwargs['lookup'])
        except ValueError:
            raise NotFound()
        module = self.get_entity_or_404(entity_set, lookup_value)
        return module
