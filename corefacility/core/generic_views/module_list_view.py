from core.entity.corefacility_module import CorefacilityModuleSet
from core.serializers import ModuleSerializer
from core.permissions import ProjectRelatedPermission

from .generics import EntityListView


class ModuleListView(EntityListView):
    """
    This is a base class for viewing all list modules
    """

    entry_point = None
    """ The entry point the module is attached to """

    entity_set_class = CorefacilityModuleSet
    list_serializer_class = ModuleSerializer
    detail_serializer_class = ModuleSerializer
    pagination_class = None
    permission_classes = [ProjectRelatedPermission]

    def list(self, request, *args, **kwargs):
        """
        Processes the module listing request
        :param request: the HTTP request
        :param args: request path arguments
        :param kwargs: request path keyword arguments
        :return: the HTTP response
        """
        response = super().list(request, *args, **kwargs)
        response.data = {"module_list": response.data}
        self.set_additional_data_info(response.data)
        return response

    def get_entry_point(self):
        """
        Returns the entry point the module is attached to
        """
        if self.entry_point is None:
            raise NotImplementedError("Please, define the entry_point property")
        return self.entry_point

    def filter_queryset(self, module_set):
        """
        Provides the module set filtration
        :param module_set: module set before all filters are applied
        :return: module set after all filters are applied
        """
        module_set.entry_point = self.get_entry_point()
        module_set.is_enabled = True
        if not self.request.user.is_superuser:
            module_set.is_application = True
        if hasattr(self.request, "project"):
            module_set.project = self.request.project
        return module_set

    def set_additional_data_info(self, response_data):
        """
        By default, the response output data contain only one field: 'module_list' that contains list of
        all modules included into the project and connected to a particular entry point. This method adds another
        field containing information about an object that shall be used for particular module
        :param response_data: a dictionary that contain all response fields and their corresponding values.
            You have to add another response fields to this dictionary
        :return: nothing. Your main goal is to change content of the response_data dictionary. Please, don't create
            another dictionary, just modify the existing one
        """
        pass
