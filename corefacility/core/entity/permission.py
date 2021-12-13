from .entity import Entity
from .entity_fields import ReadOnlyField


class Permission(Entity):
    """
    Defines the user-adjusted permission
    """

    _required_fields = ["group", "access_level"]

    _public_fields = {
        "group": ReadOnlyField(description="User group"),
        "access_level_alias": ReadOnlyField(description="Access level alias"),
        "access_level_description": ReadOnlyField(description="Access level description"),
    }

    _level_type = None
    """ Access level type that the user can set """

    def set_access_level(self, alias: str):
        """
        Sets the permission access level.
        The access level checks for its existence

        :param alias: access level alias
        :return: nothing
        """
        raise NotImplementedError("TO-DO: set_access_level")
