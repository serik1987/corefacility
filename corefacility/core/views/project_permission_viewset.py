from rest_framework.request import Request

from core.models.enums import LevelType
from core.entity.group import Group
from core.entity.entity_fields.field_managers.permission_manager import PermissionManager
from core.permissions import ProjectSettingsPermission

from .permission_viewset import PermissionViewSet


class ProjectPermissionViewSet(PermissionViewSet):
    """
    Returns the project permission
    """

    access_level_type = LevelType.project_level
    permission_classes = [ProjectSettingsPermission]

    def get_permission_set(self, request: Request) -> PermissionManager:
        """
        Returns set of permissions that has already been saved in the database and exists at the level of
        entities.

        :param request: a request sent by the user
        :return: value of the 'permissions' field for the corresponding entity
        """
        return request.project.permissions

    def is_root_group(self, request: Request, group: Group) -> bool:
        """
        Returns True if a given group is root group and False otherwise

        :param request: the HTTP request received from the client
        :param group: group to check
        :return: True if the group shall be considered as root group, False otherwise
        """
        return group.id == request.project.root_group.id
