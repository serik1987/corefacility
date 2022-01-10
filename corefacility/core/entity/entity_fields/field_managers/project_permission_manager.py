from core.models import ProjectPermission
from core.models.enums import LevelType

from .permission_manager import PermissionManager


class ProjectPermissionManager(PermissionManager):
    """
    Manages access control lists for a particular project.
    """

    _permission_model = ProjectPermission
    """ Defines particular model connects your entity model, the Group model and particular access level """

    _entity_link_field = "project_id"
    """ Defines a link that connects particular entity to the permission model mentioned above """

    _access_level_type = LevelType.project_level
    """ Accepted access level type """

    def get(self, group):
        """
        Reads access level for a certain group.

        WARNING. The method is not optimized according to the number of SQL queries. Use the 'user' filter in the
        ProjectSet for full and comprehensive information.

        :param group: a group to which access level must be set or None if access level shall be set for the rest
            of users
        :return: the AccessLevel entity reflecting a certain access level for the group.
        """
        from core.entity.entity_sets.access_level_set import AccessLevelSet

        if group is not None and self.entity.root_group is not None and group.id == self.entity.root_group.id:
            level_set = AccessLevelSet()
            level_set.type = LevelType.project_level
            level = level_set.get("full")
            return level
        else:
            return super().get(group)
