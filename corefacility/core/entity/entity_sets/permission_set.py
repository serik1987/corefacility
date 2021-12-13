from core.entity.entity_sets.entity_set import EntitySet
from core.entity.entity_fields import EntityValueManager


class PermissionSet(EntityValueManager, EntitySet):
    """
    Defines user-controlled permission to some project or application
    """

    def get(self, id=id):
        """
        Retrieves permission for certain group

        :param id: the group ID
        :return: either ProjectPermission or AppPermission
        """
        raise NotImplementedError("TO-DO: PermissionSet.get")
