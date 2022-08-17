from .entity import Entity


class ArbitraryAccessLevelEntity(Entity):
    """
    This is the base class for all entities which access can be adjusted by the superuser or the project leader
    (e.g., projects, applications).
    """

    @classmethod
    def get_access_level_hierarchy(cls):
        """
        Returns a dictionary containing access levels and their weights. If the user has two different access
        levels to the same entity, this feature will select a level with the highest weight.

        :return: a dictionary which keys are access level aliases and which values are access level weights
        """
        raise NotImplementedError("get_access_level_hierarchy")

    @classmethod
    def get_proper_access_level(cls, access_level_list):
        """
        Returns a proper access level from the list

        :param access_level_list: the access level list
        :return: proper access level
        """
        current_weight = 0.0
        current_access_level = "no_access"
        if isinstance(access_level_list, str):
            current_access_level = access_level_list
        elif isinstance(access_level_list, set):
            hierarchy = cls.get_access_level_hierarchy()
            for access_level in access_level_list:
                weight = hierarchy[access_level]
                if weight == current_weight:
                    raise ValueError("all access levels shall have clearly different weights!")
                if weight > current_weight:
                    current_weight = weight
                    current_access_level = access_level
        return current_access_level
