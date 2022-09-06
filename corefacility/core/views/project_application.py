from uuid import UUID
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from core.entity.corefacility_module import CorefacilityModuleSet
from core.entity.project_application import ProjectApplicationSet
from core.generic_views import EntityViewSet
from core.permissions import ProjectApplicationPermission
from core.serializers import ProjectApplicationSerializer


class ProjectApplicationViewSet(EntityViewSet):
    """
    Changing project application
    """

    entity_set_class = ProjectApplicationSet
    permission_classes = [ProjectApplicationPermission]
    list_serializer_class = ProjectApplicationSerializer
    detail_serializer_class = ProjectApplicationSerializer

    def filter_queryset(self, project_application_set):
        """
        Providers additional filtration of the project_application_set
        :param project_application_set:  project_application_set before the additional filtration
        :return: project_application_set after the additional filtration
        """
        project_application_set = super().filter_queryset(project_application_set)

        try:
            uuid = UUID(self.kwargs['lookup'])
        except ValueError:
            raise NotFound()
        module_set = CorefacilityModuleSet()
        module_set.is_enabled = True
        module_set.is_application = True
        module = self.get_entity_or_404(module_set, uuid)

        project_application_set.project = self.request.project
        project_application_set.application = module
        return project_application_set
