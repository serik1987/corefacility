from core.generic_views import EntityViewSet
from core.entity.project import ProjectSet
from core.serializers import ProjectListSerializer, ProjectDetailSerializer


class ProjectViewSet(EntityViewSet):
    """
    Dealing with projects
    """

    entity_set_class = ProjectSet
    list_serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
