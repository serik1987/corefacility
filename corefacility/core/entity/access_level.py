from core.models.enums import LevelType
from .entity import Entity
from .entity_sets.access_level_set import AccessLevelSet
from .entity_fields import EntityField, ReadOnlyField
from .entity_exceptions import EntityOperationNotPermitted


class AccessLevel(Entity):
    """
    Defines the access level
    """

    _entity_set_class = AccessLevelSet

    _entity_provider_list = []  # TO-DO: define the access level provider

    _required_fields = ["type", "alias", "name"]

    _public_field_description = {
        "type": ReadOnlyField(description="Access level type"),
        "alias": EntityField(str, max_length=50),
        "name": EntityField(str, max_length=64)
    }

    def create(self):
        """
        Creates new access level.
        Note that only project access levels are suitable for creation

        :return: nothing
        """
        raise NotImplementedError("TO-DO: AccessLevel.create")

    def update(self):
        """
        Changing the access level is not permitted

        :return:nothing
        """
        raise EntityOperationNotPermitted()

    def delete(self):
        """
        Deletes access level.
        Access levels installed by default are not permitted to be destroyed

        :return: nothing
        """
        raise NotImplementedError("TO-DO: AccessLevel.delete")
