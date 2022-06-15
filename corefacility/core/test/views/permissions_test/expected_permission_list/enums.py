"""
This module contains all enumerated settings
"""

from enum import Enum


class GroupMode(Enum):
    """
    This property defines the way how the user will try to change the permission
    """

    NEW_GROUP = "new_group"
    """ The user tries to add existent group to the ACL """

    SAME_GROUP = "same_group"
    """ The user tries to modify permissions for a group that has already been presented in the ACL """

    ROOT_GROUP = "root_group"
    """ The user tries to modify permissions for the root group """

    NO_GROUP = "no_group"
    """ The user has sent non-valid group ID """


class LevelMode(Enum):
    """
    This property defines what access level value the user will try to set
    """

    ANY_LEVEL = "any_level"
    """ The user will select an arbitrary access level (not recommended to use this value) """

    SAME_LEVEL = "same_level"
    """ The user will try to set the same access level that certain permission has """

    OTHER_LEVEL = "other_level"
    """ The user definitely try to change the access level for a given permission """

    BAD_LEVEL = "bad_level"
    """ The user tries to set non-valid access level """
