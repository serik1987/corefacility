from core.permissions import ProjectSettingsPermission

from .permission_viewset import PermissionViewSet


class ProjectPermissionViewSet(PermissionViewSet):
    """
    Returns the project permission
    """

    permission_classes = [ProjectSettingsPermission]
