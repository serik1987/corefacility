from .entity import Entity
from .fields import RelatedEntityField


class Permission(Entity):
    """
    Defines the user-adjusted permission
    """

    _required_fields = ["group", "access_level"]

    _public_field_description = {
        "group": RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.group.Group",
            description="User group"
        ),
        "access_level": RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.access_level.AccessLevel",
            description="Access level"
        )
    }
