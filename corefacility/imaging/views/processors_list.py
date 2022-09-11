from core.generic_views import ModuleListView
from imaging.entity import MapSet
from imaging.entity.entry_points.processors import ProcessorsEntryPoint
from imaging.serializers import MapSerializer


class ProcessorsListView(ModuleListView):
    """
    List of all imaging processors
    """

    def get_entry_point(self):
        """
        Returns the entry point the module is attached to
        """
        return ProcessorsEntryPoint()

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
        try:
            map_lookup = int(self.kwargs['map_lookup'])
        except ValueError:
            map_lookup = self.kwargs['map_lookup']
        map_set = MapSet()
        map_set.project = self.request.project
        functional_map = self.get_entity_or_404(map_set, map_lookup)
        map_serializer = MapSerializer(functional_map)
        response_data['map_info'] = map_serializer.data
