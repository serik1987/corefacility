from .entity import Entity
from .entity_sets.group_set import GroupSet
from .entity_fields import EntityField, RelatedEntityField, ManagedEntityField
from .entity_fields.user_manager import UserManager
from .entity_providers.model_providers.group_provider import GroupProvider as ModelProvider


class Group(Entity):
    """
    Defines the scientific group of users.

    The scientific group is a minimal user unit that is used for access management
    """

    _entity_set_class = GroupSet

    _entity_provider_list = [ModelProvider()]

    _required_fields = ["name", "governor"]

    _public_field_description = {
        "name": EntityField(str, min_length=1, max_length=256,
                            description="Group name"),
        "governor": RelatedEntityField("core.entity.user.User",
                                       description="The group leader"),
        "users": ManagedEntityField(UserManager,
                                    description="Users containing in the group"),
    }

    def __eq__(self, other):
        """
        Compares two scientific groups

        :param other: the other scientific group
        :return: True if two scientific groups are equal
        """
        if not isinstance(other, Group):
            return False
        if self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.governor != other.governor:
            return False
        return True
