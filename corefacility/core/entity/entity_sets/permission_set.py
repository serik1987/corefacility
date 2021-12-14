from core.entity.entity_sets.entity_set import EntitySet
from core.entity.entity_fields import EntityValueManager


class PermissionSet(EntityValueManager, EntitySet):
    """
    Defines user-controlled permission to some project or application
    """

    def __init__(self, value, default_value=None):
        """
        Initializes the permission set
        """
        super().__init__(value, default_value=default_value)
        self._entity_filters = {}

    def get(self, id=id):
        """
        Retrieves permission for certain group

        :param id: the group ID
        :return: either ProjectPermission or AppPermission
        """
        raise NotImplementedError("TO-DO: PermissionSet.get")
