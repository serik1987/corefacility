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

    superuser_required = True
    ordinary_user_required = True

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
            :param level_name: human-readable name of the access level
            """
            self.group_id = group_id
            self.group_name = group_name
            self.level_alias = level_alias

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_entity_set_objects()
        cls.authorize_test_users()

    @classmethod
    def create_entity_set_objects(cls):
        cls.user_set_object = UserSetObject()
        cls.group_set_object = GroupSetObject(cls.user_set_object.clone())
        cls.project_set_object = ProjectSetObject(cls.group_set_object)

    @classmethod
    def authorize_test_users(cls):
        from core.entity.entry_points.authorizations import AuthorizationModule
        for user in cls.user_set_object:
            token = AuthorizationModule.issue_token(user)
            setattr(cls, user.login + "_token", token)


del BaseViewTest
