from rest_framework import status
from parameterized import parameterized

from .base_test_class import BasePermissionTest


def permission_list_provider():
    """
    Provides data for permission list

    :return: list of arguments for the test_permission_list function
    """
    hhna_level_list = []

    return [
        ("superuser", "hhna", status.HTTP_200_OK, hhna_level_list),
        ("user1", "hhna", status.HTTP_403_FORBIDDEN, hhna_level_list),
        ("user2", "hhna", status.HTTP_200_OK, hhna_level_list),
        ("user3", "hhna", status.HTTP_403_FORBIDDEN, hhna_level_list),
        ("user6", "hhna", status.HTTP_403_FORBIDDEN, hhna_level_list),
        *[
            (login, "hhna", status.HTTP_404_NOT_FOUND, hhna_level_list)
            for login in ("user4", "user5", "user7", "user8", "user9", "user10", "ordinary_user")
        ],
        [None, "hhna", status.HTTP_401_UNAUTHORIZED, hhna_level_list],
    ]


class TestProjectPermissions(BasePermissionTest):
    """
    Contains test routines for project permissions
    """

    @parameterized.expand(permission_list_provider())
    def test_permission_list(self, token_id, project_alias, expected_status_code, expected_permission_list):
        """
        Tests the project permission list

        :param token_id: a string that will be used for finding the user authorization token. The authorization
            token shall be the value of <token_id>_token field
        :param project_alias: alias for a particular project within the project set
        :param expected_status_code: status code to be expected
        :param expected_permission_list: list of tuples corresponding to permission rights
        :return: nothing
        """
        path = self.get_permission_list_path(project_alias)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            print(token_id, project_alias, response.data, expected_permission_list)

    def get_permission_list_path(self, project_alias):
        """
        Returns the permission path

        :param project_alias: project alias to be used
        :return: full permission path
        """
        return "/api/{version}/projects/{alias}/permissions/".format(version=self.API_VERSION, alias=project_alias)


del BasePermissionTest
