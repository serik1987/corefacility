from core.models.enums import LevelType

from .entity import Entity
from .entity_sets.access_level_set import AccessLevelSet
from .entity_providers.model_providers.access_level_provider import AccessLevelProvider
from .entity_fields import EntityField, ReadOnlyField, EntityAliasField


class AccessLevel(Entity):
    """
    Defines the access level
    """

    _entity_set_class = AccessLevelSet

    _entity_provider_list = [AccessLevelProvider()]  # TO-DO: define the access level provider

    _required_fields = ["type", "alias", "name"]

    _public_field_description = {
        "type": ReadOnlyField(description="Access level type"),
        "alias": EntityAliasField(max_length=50),
        "name": EntityField(str, min_length=1, max_length=64, description="Access level name")
    }

    def __init__(self, **kwargs):
        """
        Initializes the access level

        :param kwargs: access level field values
        """
        super().__init__(**kwargs)
        if self._type is None:
            self._type = LevelType.app_level
