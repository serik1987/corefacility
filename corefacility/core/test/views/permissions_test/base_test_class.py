from typing import List, Tuple
import random

from rest_framework import status
from rest_framework.response import Response

from core.entity.access_level import AccessLevelSet
from core.entity.group import Group
from core.views.permission_viewset import PermissionViewSet

from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject

from ..base_view_test import BaseViewTest


class BasePermissionTest(BaseViewTest):
    """
    This is the base class for testing i/o requests for project and application permissions.
    """

    user_set_object = None
    group_set_object = None
    project_set_object = None
    access_levels = None

    superuser_required = True
    ordinary_user_required = True

    access_level_type = None
    """ Either 'prj' or 'app' """

    class PermissionListItem:
        """
        An item containing information about the permission list
        """

        group_id = None
        group_name = None
        level_alias = None

        def __init__(self, group_id=None, group_name=None, level_alias=None):
            """
            Creates new permission list item

            :param group_id: ID of the permitting group
            :param group_name: name of the permitting group
            :param level_alias: human-readable name of the access level
            """
            self.group_id = group_id
            self.group_name = group_name
            self.level_alias = level_alias

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_entity_set_objects()
        cls.authorize_test_users()
        cls.load_access_levels()

    @classmethod
    def create_entity_set_objects(cls):
        cls.user_set_object = UserSetObject()
        cls.group_set_object = GroupSetObject(cls.user_set_object.clone())
        cls.project_set_object = ProjectSetObject(cls.group_set_object.clone())

    @classmethod
    def authorize_test_users(cls):
        from core.entity.entry_points.authorizations import AuthorizationModule
        for user in cls.user_set_object:
            token = AuthorizationModule.issue_token(user)
            setattr(cls, user.login + "_token", token)

    @classmethod
    def load_access_levels(cls):
        cls.access_levels = {}
        level_set = AccessLevelSet()
        level_set.type = cls.access_level_type
        for level in level_set:
            cls.access_levels[level.alias] = level

    def setUp(self):
        super().setUp()
        PermissionViewSet.throttle_classes = []

    def permission_list_response_to_permission_list(self, response: Response) -> list:
        """
        Converts the permission list response to the list of PermissionListItem's instances.
        Assertion for response status code equal to 200 will also be performed

        :param response: the response received
        :return: list of permission items.
        """
        self.assertEquals(response.status_code, status.HTTP_200_OK, "An auxiliary response status code must be 200")
        permission_list = []
        for permission_info in response.data:
            permission = self.PermissionListItem(group_id=permission_info['group_id'],
                                                 group_name=permission_info['group_name'],
                                                 level_alias=permission_info['access_level_alias'])
            permission_list.append(permission)
        return permission_list

    def choose_permission_group(self, permission_list: List[PermissionListItem], group_mode: str,
                                root_group: Group, group_add_allowed: bool = True) -> Tuple[int, int]:
        """
        Chooses a particular group and some random access level. Also, the function adds the selected permission to
        the permission list

        :param permission_list: permission list from which the group shall be chosen
        :param group_mode: 'new_group' for selection for a group not presented in the permission_list,
            'same_group' if the group shall be presented in the group list
        :param root_group: a group that shall not be selected in any way
        :param group_add_allowed: True if the group add is allowed by the routine, False otherwise
        :return: Updated permission list item
        """
        group_set = {item.group_id for item in permission_list}
        if group_mode == "new_group":
            full_group_set = {group.id for group in self.group_set_object}
            group_set = full_group_set - group_set - {root_group.id}
        assert len(group_set) > 0
        group_id = random.choice(list(group_set))
        level_alias = random.choice(list(self.access_levels.keys()))
        level_id = self.access_levels[level_alias].id
        permission = None
        for current_permission in permission_list:
            if current_permission.group_id == group_id:
                assert group_mode == "same_group"
                permission = current_permission
        if permission is None and group_add_allowed:
            assert group_mode == "new_group"
            group_name = self.group_set_object.get_by_id(group_id).name
            permission = self.PermissionListItem(group_id=group_id, group_name=group_name, level_alias=level_alias)
            permission_list.append(permission)
        if permission is not None:
            permission.level_alias = level_alias
        return group_id, level_id

    def assert_permission_list_response(self, response: Response, expected_status_code: int,
                                        expected_permission_list: list):
        """
        Asserts that the permission list response is the same as some expected one

        :param response: the response itself
        :param expected_status_code: expected status code of the response
        :param expected_permission_list: for 2xx responses the expected permission list containing in  the responses
            for other responses this argument is ignored
        :return: nothing
        """
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            self.assertEquals(len(response.data), len(expected_permission_list),
                              "Unexpected length of the Access Control List")
            for index in range(len(response.data)):
                actual_permission = response.data[index]
                expected_permission = expected_permission_list[index]
                expected_group_id = self.group_set_object[expected_permission.group_id].id
                self.assertEquals(actual_permission['group_id'], expected_group_id, "Unexpected group ID")
                self.assertEquals(actual_permission['group_name'], expected_permission.group_name,
                                  "Unexpected group name")
                self.assertEquals(actual_permission['access_level_alias'], expected_permission.level_alias,
                                  "Unexpected access level alias")
                expected_level = self.access_levels[expected_permission.level_alias]
                self.assertEquals(actual_permission['access_level_id'], expected_level.id,
                                  "Unexpected access level ID")
                self.assertEquals(actual_permission['access_level_name'], expected_level.name,
                                  "Unexpected access level name")

    def assert_permission_updated(self, permission_manager, expected_permission_list, root_group):
        """
        Asserts that a given permission has been updated.

        :param permission_manager: permission manager to check whether a given permission is within the database
        :param expected_permission_list: list of all permissions that are expected to be in the database
        :param root_group: True for the root group, False otherwise
        :return: nothing
        """
        for group in self.group_set_object:
            if group.id == root_group.id:
                self.assertEquals(permission_manager.get(group).alias, "full", "Full access shall be provided "
                                                                         "for the root group")
            else:
                perm = None
                for permission in expected_permission_list:
                    if permission.group_id == group.id:
                        perm = permission
                        break
                if perm is None:
                    self.assertEquals(permission_manager.get(group).alias, "no_access",
                                      "No access is expected to be provided for a group " + group.name)
                else:
                    self.assertEquals(permission_manager.get(group).alias, perm.level_alias,
                                      "Unexpected access level for a group " + group.name)


del BaseViewTest
