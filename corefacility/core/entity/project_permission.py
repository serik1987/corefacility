from core.models.enums import LevelType
from .permission import Permission
from .entity_sets.project_permission_set import ProjectPermissionSet


class ProjectPermission(Permission):
    """
    Defines the project permission
    """

    _entity_set_class = ProjectPermissionSet

    _entity_provider_list = []  # TO-DO: define proper entity providers

    _level_type = LevelType.project_level
