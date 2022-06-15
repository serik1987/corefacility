from typing import List, Tuple
import random

from rest_framework import status
from rest_framework.response import Response

from core.entity.access_level import AccessLevelSet
from core.entity.entity_fields.field_managers.permission_manager import PermissionManager
from core.views.permission_viewset import PermissionViewSet

from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject

from ..base_view_test import BaseViewTest
from .expected_permission_list import ExpectedPermission, ExpectedPermissionList, PermissionListSimulator
from .expected_permission_list.enums import GroupMode, LevelMode


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

    def assert_permission_updated(self, permission_manager: PermissionManager,
                                  expected_permission_list: ExpectedPermissionList):
        """
        Asserts that a given permission has been updated.

        :param permission_manager: permission manager to check whether a given permission is within the database
        :param expected_permission_list: list of all permissions that are expected to be in the database
        :return: nothing
        """
        for group in self.group_set_object:
            if group.id == expected_permission_list.root_group.id:
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
