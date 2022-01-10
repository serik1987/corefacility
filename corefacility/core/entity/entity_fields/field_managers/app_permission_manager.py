from .permission_manager import PermissionManager


class AppPermissionManager(PermissionManager):
    """
    Defines the application permission manager.
    """

    _permission_model = "core.models.AppPermission"
