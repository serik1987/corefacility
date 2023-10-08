from ..generic_views import ModuleListView
from ..entry_points import ProjectsEntryPoint
from ..serializers import ProjectDetailSerializer


class ProjectModulesListView(ModuleListView):
    """
    Downloading list of all modules attached to the processors entry point
    """

    def get_entry_point(self):
        """
        The entry point which modules shall be listed
        """
        return ProjectsEntryPoint()

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
        project_serializer = ProjectDetailSerializer(self.request.project, context={"request": self.request})
        response_data["project_info"] = project_serializer.data
