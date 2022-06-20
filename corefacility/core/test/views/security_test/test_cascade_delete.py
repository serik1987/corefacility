from parameterized import parameterized
from rest_framework import status

from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from ..base_view_test import BaseViewTest


def user_login_provider():
    """
    Provides data for all tests
    """
    return [("user%d" % n,) for n in range(1, 11)]


def group_index_provider():
    """
    Provides indices for all groups
    """
    return [(group_index,) for group_index in range(5)]


def safe_delete_provider():
    """
    Provides the data for safe delete (i.e., delete the user plus delete all groups where the user is governor)
    """
    return [
        ("user1", status.HTTP_204_NO_CONTENT),
        ("user2", status.HTTP_400_BAD_REQUEST),
        ("user3", status.HTTP_204_NO_CONTENT),
        ("user4", status.HTTP_400_BAD_REQUEST),
        ("user5", status.HTTP_400_BAD_REQUEST),
        ("user6", status.HTTP_204_NO_CONTENT),
        ("user7", status.HTTP_204_NO_CONTENT),
        ("user8", status.HTTP_400_BAD_REQUEST),
        ("user9", status.HTTP_204_NO_CONTENT),
        ("user10", status.HTTP_204_NO_CONTENT),
    ]


class TestCascadeDelete(BaseViewTest):
    """
    Test routines for the user cascade delete
    """

    superuser_required = True
    ordinary_user_required = False

    user_delete_path = "/api/{version}/users/{login}/"
    group_delete_path = "/api/{version}/groups/{id}/"

    def test_delete_himself(self):
        """
        Tests whether the user can delete himself

        :return: nothing
        """
        self.delete_user("superuser", status.HTTP_403_FORBIDDEN)

    @parameterized.expand(safe_delete_provider())
    def test_cascade_user_delete_safe(self, login, expected_status):
        """
        Tests the safe cascade delete for a user

        :param login: login for the deleted user
        :param expected_status: expected status code
        :return: nothing
        """
        user_set_object = UserSetObject()
        GroupSetObject(user_set_object)
        self.delete_user(login, expected_status)

    @parameterized.expand(user_login_provider())
    def test_cascade_user_delete_force_group(self, login):
        """
        Tests the force delete for a user

        :param login: login for the deleted user
        :return: nothing
        """
        user_set_object = UserSetObject()
        GroupSetObject(user_set_object)
        self.delete_user(login, status.HTTP_204_NO_CONTENT, True)

    @parameterized.expand(user_login_provider())
    def test_cascade_user_delete_force_project(self, login):
        """
        Tests the force delete for a user given that the user has already created a couple of
        projects

        :param login: login for the deleted user
        :return: nothing
        """
        user_set_object = UserSetObject()
        group_set_object = GroupSetObject(user_set_object)
        ProjectSetObject(group_set_object)
        self.delete_user(login, status.HTTP_204_NO_CONTENT, is_force=True)

    @parameterized.expand(group_index_provider())
    def test_cascade_group_delete_safe_positive(self, group_index):
        """
        Tests the safe group delete (positive test cases)

        :param group_index: index of a group in the group object
        :return: nothing
        """
        user_set_object = UserSetObject()
        group_set_object = GroupSetObject(user_set_object)
        self.delete_group(group_set_object[group_index], status.HTTP_204_NO_CONTENT)

    @parameterized.expand(group_index_provider())
    def test_cascade_group_delete_safe_negative(self, group_index):
        """
        Tests the safe group delete (negative test cases)

        :param group_index: index of a group in the group object
        :return: nothing
        """
        user_set_object = UserSetObject()
        group_set_object = GroupSetObject(user_set_object)
        ProjectSetObject(group_set_object)
        self.delete_group(group_set_object[group_index], status.HTTP_400_BAD_REQUEST)

    @parameterized.expand(group_index_provider())
    def test_cascade_group_delete_force(self, group_index):
        """
        Tests the force group delete

        :param group_index: index of a group in the group object
        :return: nothing
        """
        user_set_object = UserSetObject()
        group_set_object = GroupSetObject(user_set_object)
        ProjectSetObject(group_set_object)
        self.delete_group(group_set_object[group_index], status.HTTP_204_NO_CONTENT, is_force=True)

    def delete_user(self, login, expected_status, is_force=False):
        """
        Deletes the user and checks whether such delete is successful

        :param login: login of a user to be deleted
        :param expected_status: expected status code
        :param is_force: True for force delete, False for sage delete
        :return: nothing
        """
        user_delete_path = self.user_delete_path.format(version=self.API_VERSION, login=login)
        if is_force:
            user_delete_path += "?force"
        headers = self.get_authorization_headers("superuser")
        response = self.client.delete(user_delete_path, **headers)
        self.assertEquals(response.status_code, expected_status, "Unexpected status code")
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertEquals(response.data["code"], "GroupGovernorConstraintFails",
                              "Group contraint failure has been processed successfully but information about "
                              "the error containing in the response body is not correct")

    def delete_group(self, group, expected_status, is_force=False):
        """
        Deletes the group

        :param group: the group to be deleted
        :param expected_status: expected status code
        :param is_force: True for force delete, False for safe delete
        :return: nothing
        """
        group_delete_path = self.group_delete_path.format(version=self.API_VERSION, id=group.id)
        if is_force:
            group_delete_path += "?force"
        headers = self.get_authorization_headers("superuser")
        response = self.client.delete(group_delete_path, **headers)
        self.assertEquals(response.status_code, expected_status, "Unexpected status code")
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertEquals(response.data["code"], "ProjectRootGroupConstraintFails",
                              "Unexpected information about the error happened")


del BaseViewTest
