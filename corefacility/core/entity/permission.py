from .entity import Entity
from .entity_fields import ReadOnlyField, RelatedEntityField, EntityField, EntityAliasField


class Permission(Entity):
    """
    Defines the user-adjusted permission
    """

    _required_fields = ["group", "access_level"]

    _public_field_description = {
        "group": RelatedEntityField("core.entity.group.Group", description="User group"),
        "access_level": RelatedEntityField("core.entity.access_level.AccessLevel", description="Access level")
    }
