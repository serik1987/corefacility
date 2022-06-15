from typing import Any, Union
import random

from .expected_permission_list import ExpectedPermission, ExpectedPermissionList
from .enums import GroupMode, LevelMode
from .exceptions import DataProviderError


class PermissionListSimulator:
    """
    Simulates the CRUD operations with the permission list and calculates the expected permission lists
    """

    _permission_list = None
    _group_set_object = None
    _access_levels = None
    _group_mode = None
    _group_add_allowed = None
    _status_code_ok = None
    _level_mode = None

    _group_id = None
    _permission = None
    _access_level_alias = None
    _access_level_id = None

    @staticmethod
    def assert_condition(condition: bool):
        """
        Raises an exception if the condition doesn't hold

        :param condition: the condition to check
        :return: nothing
        """
        if not condition:
            raise DataProviderError()

    def __init__(self, parent: Any, permission_list: ExpectedPermissionList, group_mode: Union[GroupMode, str],
                 group_add_allowed: bool = True, status_code_ok: bool = True,
                 level_mode: Union[LevelMode, str] = LevelMode.ANY_LEVEL):
        """
        Initializes the simulator. This is important for simulator to contain 'group_set_object' class

        :param parent: any TestCase class that calls the simulator
        :param permission_list: Permission list which the simulator works on
        :param group_mode: defines which group the simulator tries to add
        :param group_add_allowed: True if the tested feature allows to add groups to the Access Control List (ACL),
            False if the feature allowes to modify the ACL
        :param status_code_ok: True if the simulated action shall be successful, False if the action shall left
            the ACL intact
        :param level_mode: Defines the access value the user is trying to set
        """
        self._permission_list = permission_list
        self._group_set_object = parent.group_set_object
        self._access_levels = parent.access_levels
        self._group_mode = GroupMode(group_mode)
        self._group_add_allowed = group_add_allowed
        self._status_code_ok = status_code_ok
        self._level_mode = LevelMode(level_mode)

    @property
    def permission_list(self):
        """
        Permission list the simulator works on
        """
        return self._permission_list

    @property
    def group_id(self):
        """
        ID of a group the user is trying to test
        """
        if self._group_id is None:
            self.set_random_group()
        return self._group_id

    @property
    def permission(self):
        """
        Permission the user is trying to change
        """
        if self._permission is None:
            self._permission = self.permission_list.get_by_group_id(self.group_id)
        return self._permission

    @property
    def access_level_alias(self):
        """
        Alias for the access level
        """
        if self._access_level_alias is None:
            self.set_random_access_level(self.permission)
        return self._access_level_alias

    @property
    def access_level_id(self):
        """
        Alias for access level ID
        """
        if self._access_level_id is None:
            self.set_random_access_level(self.permission)
        return self._access_level_id

    def set_random_group(self) -> int:
        """
        Sets the permission random group

        :return: the group ID
        """
        permission_group_set = {item.group_id for item in self.permission_list}
        full_group_set = {group.id for group in self._group_set_object}
        if self._group_mode == GroupMode.NEW_GROUP:
            result_set = full_group_set - permission_group_set - {self.permission_list.root_group.id}
            self.assert_condition(len(result_set) > 0)
            self._group_id = random.choice(list(result_set))
        elif self._group_mode == GroupMode.SAME_GROUP:
            self.assert_condition(len(permission_group_set) > 0)
            self._group_id = random.choice(list(permission_group_set))
        elif self._group_mode == GroupMode.ROOT_GROUP:
            self._group_id = self.permission_list.root_group.id
        elif self._group_mode == GroupMode.NO_GROUP:
            self._group_id = max(full_group_set) + 1
        else:
            raise ValueError("Incorrect value of the group_mode")
        return self._group_id

    def set_random_access_level(self, permission: ExpectedPermission) -> int:
        """
        Sets the access level the user is trying to set

        :param permission: the permission which access level is trying to be edited
        :return: the access level ID itself
        """
        self.assert_condition(self._group_mode == GroupMode.SAME_GROUP or permission is None)
        available_levels = set(self._access_levels.keys())
        if self._group_mode == GroupMode.ROOT_GROUP:
            permission_level = "full"
        else:
            permission_level = permission.level_alias if permission is not None else "bad"
        if self._level_mode == LevelMode.SAME_LEVEL:
            level_alias = permission_level
        elif self._level_mode == LevelMode.OTHER_LEVEL:
            valid_levels = available_levels - {permission_level}
            self.assert_condition(len(valid_levels) > 0)
            level_alias = random.choice(list(valid_levels))
        elif self._level_mode == LevelMode.BAD_LEVEL:
            level_alias = "bad"
        elif self._level_mode == LevelMode.ANY_LEVEL:
            level_alias = random.choice(list(available_levels))
        else:
            raise ValueError("Incorrect value of the level_mode")
        self._access_level_alias = level_alias
        self._access_level_id = self._access_levels[level_alias].id if level_alias != "bad" else 100
        return self._access_level_id

    def simulate_permission_set(self):
        """
        Changes the expected ACL

        :return: nothing
        """
        if self._status_code_ok:
            if self.permission is None and self._group_add_allowed:
                self.assert_condition(self._group_mode == GroupMode.NEW_GROUP)
                group_name = self._group_set_object.get_by_id(self.group_id).name
                self._permission = ExpectedPermission(group_id=self.group_id, group_name=group_name,
                                                      level_alias=self.access_level_alias)
                self.permission_list.append(self.permission)
            elif self.permission is not None:
                self.permission.level_alias = self.access_level_alias

    def simulate_permission_delete(self):
        """
        Deletes an arbitrary item from the ACL

        :return: nothing
        """
        if self._status_code_ok and self.permission is not None:
            try:
                self.permission_list.remove(self.permission)
            except ValueError:
                raise DataProviderError()
