from core.models.enums import LevelType
from .permission import Permission
from .entity_sets.app_permission_set import AppPermissionSet


class AppPermission(Permission):
    """
    Defines the application permission
    """

    _entity_set_class = AppPermissionSet

    _entity_provider_list = []  # TO-DO: Define proper entity providers

    _level_type = LevelType.app_level
