from rest_framework.response import Response

from core.generic_views import EntityViewSet
from core.permissions import ProjectApplicationPermission
from core.serializers import ProjectApplicationSerializer


class ProjectApplicationViewSet(EntityViewSet):
    """
    Changing project application
    """

    permission_classes = [ProjectApplicationPermission]
    list_serializer_class = ProjectApplicationSerializer
    detail_serializer_class = ProjectApplicationSerializer
