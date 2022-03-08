from core.entity.entity_exceptions import EntityOperationNotPermitted

from .permission_manager import PermissionManager


class AppPermissionManager(PermissionManager):
    """
    Defines the application permission manager.
    """

    _permission_model = "core.models.AppPermission"

    _access_level_type = "app"

    _entity_link_field = "application_id"

    _permission_table = "core_apppermission"

    no_access_permission = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.entity.access_level import AccessLevelSet
        self.no_access_permission = AccessLevelSet.application_level("no_access")

    def _get_entity_id(self, entity):
        """
        Returns the entity ID.

        :return: the entity id
        """
        return entity.uuid

    def _check_system_permissions(self, group, access_level):
        """
        Checks whether permission list can be changed

        :param group: the group level or None if no group specified
        :param access_level: the access level or None if no access specified
        :return: nothing
        """
        super()._check_system_permissions(group, access_level)
        if not self.entity.is_application:
            raise EntityOperationNotPermitted()

    def __iter__(self):
        """
        Iterates over all permission set
        """
        none_group_detected = False
        for group, access_level in super().__iter__():
            if group is None:
                none_group_detected = True
            yield group, access_level
        if not none_group_detected:
            yield None, self.no_access_permission
