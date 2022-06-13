from .entity import Entity
from .entity_fields import ReadOnlyField, RelatedEntityField, EntityField, EntityAliasField


class Permission(Entity):
    """
    Defines the user-adjusted permission
    """

    _required_fields = ["group", "access_level_id"]

    _public_field_description = {
        "group": RelatedEntityField("core.entity.group.Group", description="A user's group this permission is about"),
        "access_level_id": EntityField(int, description="Access level ID"),
        "access_level_alias": EntityAliasField(),
        "access_level_name": EntityField(str, description="Human-readable name"),
    }

    _level_type = None
    """ Access level type that the user can set """

    def __init__(self, **kwargs):
        """
        Initializes the entity. The entity can be initialized in the following ways:

        1) Entity(field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by another entities, request views and serializers.
        all values passed to the entity constructor will be validated

        2) Entity(_src=some_external_object, id=value0, field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by entity providers when they try to wrap the object.
        See EntityProvider.wrap_entity for details

        :param kwargs: the fields you want to assign to entity properties
        """
        if "access_level" in kwargs:
            kwargs["access_level_id"] = kwargs["access_level"].id
            kwargs["access_level_alias"] = kwargs["access_level"].alias
            kwargs["access_level_name"] = kwargs["access_level"].name
            del kwargs["access_level"]
        super().__init__(**kwargs)

    def set_access_level(self, alias: str):
        """
        Sets the permission access level.
        The access level checks for its existence

        :param alias: access level alias
        :return: nothing
        """
        raise NotImplementedError("TO-DO: set_access_level")
