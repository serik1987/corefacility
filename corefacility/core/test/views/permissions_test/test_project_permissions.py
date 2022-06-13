from rest_framework import status
from parameterized import parameterized

from core.models.enums import LevelType

from .base_test_class import BasePermissionTest


def permission_list_provider():
    """
    Provides data for permission list

    :return: list of arguments for the test_permission_list function
    """
    empty_access_list = []

    cnl_access_list = [
        BasePermissionTest.PermissionListItem(group_id=1, group_name="Своеобразные", level_alias="data_process")
    ]

    mnl_access_list = [
        BasePermissionTest.PermissionListItem(group_id=0, group_name="Сёстры Райт", level_alias="data_full"),
        BasePermissionTest.PermissionListItem(group_id=2, group_name="Управляемый хаос", level_alias="data_view"),
    ]

    mn_access_list = [
        BasePermissionTest.PermissionListItem(group_id=0, group_name="Сёстры Райт", level_alias="data_add"),
        BasePermissionTest.PermissionListItem(group_id=2, group_name="Управляемый хаос", level_alias="no_access"),
    ]

    nsw_access_list = [
        BasePermissionTest.PermissionListItem(group_id=3, group_name="Изгибно-крутильный флаттер",
                                              level_alias="data_add")
    ]

    n_access_list = [
        BasePermissionTest.PermissionListItem(group_id=2, group_name="Управляемый хаос", level_alias="full")
    ]

    nl_access_list = [
        BasePermissionTest.PermissionListItem(group_id=4, group_name="Революция сознания", level_alias="data_view")
    ]

    gcn_access_list = [
        BasePermissionTest.PermissionListItem(group_id=3, group_name="Изгибно-крутильный флаттер",
                                              level_alias="data_process")
    ]

    return [
        ["superuser", "hhna", status.HTTP_200_OK, empty_access_list],
        ["user1", "hhna", status.HTTP_403_FORBIDDEN, empty_access_list],
        ["user2", "hhna", status.HTTP_200_OK, empty_access_list],
        ["user3", "hhna", status.HTTP_403_FORBIDDEN, empty_access_list],
        ["user6", "hhna", status.HTTP_403_FORBIDDEN, empty_access_list],
        *[
            (login, "hhna", status.HTTP_404_NOT_FOUND, empty_access_list)
            for login in ("user4", "user5", "user7", "user8", "user9", "user10", "ordinary_user")
        ],
        [None, "hhna", status.HTTP_401_UNAUTHORIZED, empty_access_list],

        ["superuser", "cnl", status.HTTP_200_OK, cnl_access_list],
        ["user1", "cnl", status.HTTP_403_FORBIDDEN, cnl_access_list],
        ["user2", "cnl", status.HTTP_200_OK, cnl_access_list],
        ["user3", "cnl", status.HTTP_403_FORBIDDEN, cnl_access_list],
        ["user4", "cnl", status.HTTP_403_FORBIDDEN, cnl_access_list],
        ["user5", "cnl", status.HTTP_403_FORBIDDEN, cnl_access_list],
        ["user6", "cnl", status.HTTP_403_FORBIDDEN, cnl_access_list],
        *[
            (login, "cnl", status.HTTP_404_NOT_FOUND, cnl_access_list)
            for login in ["user8", "user9", "user10", "ordinary_user"]
        ],

        ["superuser", "mnl", status.HTTP_200_OK, mnl_access_list],
        ["user1", "mnl", status.HTTP_403_FORBIDDEN, mnl_access_list],
        ["user2", "mnl", status.HTTP_403_FORBIDDEN, mnl_access_list],
        ["user3", "mnl", status.HTTP_403_FORBIDDEN, mnl_access_list],
        ["user4", "mnl", status.HTTP_200_OK, mnl_access_list],
        ["user5", "mnl", status.HTTP_403_FORBIDDEN, mnl_access_list],
        ["user6", "mnl", status.HTTP_403_FORBIDDEN, mnl_access_list],
        ["user7", "mnl", status.HTTP_403_FORBIDDEN, mnl_access_list],
        ["user8", "mnl", status.HTTP_404_NOT_FOUND, mnl_access_list],
        ["user9", "mnl", status.HTTP_404_NOT_FOUND, mnl_access_list],
        ["user10", "mnl", status.HTTP_404_NOT_FOUND, mnl_access_list],
        ["ordinary_user", "mnl", status.HTTP_404_NOT_FOUND, mnl_access_list],

        ["superuser", "mn", status.HTTP_200_OK, mn_access_list],
        ["user1", "mn", status.HTTP_403_FORBIDDEN, mn_access_list],
        ["user2", "mn", status.HTTP_403_FORBIDDEN, mn_access_list],
        ["user3", "mn", status.HTTP_403_FORBIDDEN, mn_access_list],
        ["user4", "mn", status.HTTP_200_OK, mn_access_list],
        ["user5", "mn", status.HTTP_403_FORBIDDEN, mn_access_list],
        ["user6", "mn", status.HTTP_403_FORBIDDEN, mn_access_list],
        ["user7", "mn", status.HTTP_404_NOT_FOUND, mn_access_list],
        ["user8", "mn", status.HTTP_404_NOT_FOUND, mn_access_list],
        ["user9", "mn", status.HTTP_404_NOT_FOUND, mn_access_list],
        ["user10", "mn", status.HTTP_404_NOT_FOUND, mn_access_list],
        ["ordinary_user", "mn", status.HTTP_404_NOT_FOUND, mn_access_list],

        ["superuser", "nsw", status.HTTP_200_OK, nsw_access_list],
        ["user1", "nsw", status.HTTP_404_NOT_FOUND, nsw_access_list],
        ["user2", "nsw", status.HTTP_404_NOT_FOUND, nsw_access_list],
        ["user3", "nsw", status.HTTP_404_NOT_FOUND, nsw_access_list],
        ["user4", "nsw", status.HTTP_403_FORBIDDEN, nsw_access_list],
        ["user5", "nsw", status.HTTP_200_OK, nsw_access_list],
        ["user6", "nsw", status.HTTP_403_FORBIDDEN, nsw_access_list],
        ["user7", "nsw", status.HTTP_403_FORBIDDEN, nsw_access_list],
        ["user8", "nsw", status.HTTP_403_FORBIDDEN, nsw_access_list],
        ["user9", "nsw", status.HTTP_403_FORBIDDEN, nsw_access_list],
        ["user10", "nsw", status.HTTP_404_NOT_FOUND, nsw_access_list],
        ["ordinary_user", "nsw", status.HTTP_404_NOT_FOUND, nsw_access_list],

        ["superuser", "n", status.HTTP_200_OK, n_access_list],
        ["user1", "n", status.HTTP_404_NOT_FOUND, n_access_list],
        ["user2", "n", status.HTTP_404_NOT_FOUND, n_access_list],
        ["user3", "n", status.HTTP_404_NOT_FOUND, n_access_list],
        ["user4", "n", status.HTTP_403_FORBIDDEN, n_access_list],
        ["user5", "n", status.HTTP_200_OK, n_access_list],
        ["user6", "n", status.HTTP_403_FORBIDDEN, n_access_list],
        ["user7", "n", status.HTTP_403_FORBIDDEN, n_access_list],
        ["user8", "n", status.HTTP_200_OK, n_access_list],
        ["user9", "n", status.HTTP_403_FORBIDDEN, n_access_list],
        ["user10", "n", status.HTTP_404_NOT_FOUND, n_access_list],
        ["ordinary_user", "n", status.HTTP_404_NOT_FOUND, n_access_list],

        ["superuser", "nl", status.HTTP_200_OK, nl_access_list],
        *[
            [login, "nl", status.HTTP_404_NOT_FOUND, nl_access_list]
            for login in ("user1", "user2", "user3", "user4", "user5", "ordinary_user")
        ],
        ["user6", "nl", status.HTTP_403_FORBIDDEN, nl_access_list],
        ["user7", "nl", status.HTTP_403_FORBIDDEN, nl_access_list],
        ["user8", "nl", status.HTTP_200_OK, nl_access_list],
        ["user9", "nl", status.HTTP_403_FORBIDDEN, nl_access_list],
        ["user10", "nl", status.HTTP_403_FORBIDDEN, nl_access_list],

        ["superuser", "gcn", status.HTTP_200_OK, gcn_access_list],
        ["user6", "gcn", status.HTTP_403_FORBIDDEN, gcn_access_list],
        ["user7", "gcn", status.HTTP_403_FORBIDDEN, gcn_access_list],
        ["user8", "gcn", status.HTTP_200_OK, gcn_access_list],
        ["user9", "gcn", status.HTTP_403_FORBIDDEN, gcn_access_list],
        ["user10", "gcn", status.HTTP_403_FORBIDDEN, gcn_access_list],
        *[
            [login, "gcn", status.HTTP_404_NOT_FOUND, gcn_access_list]
            for login in ("user1", "user2", "user3", "user4", "user5", "ordinary_user")
        ],

        ["superuser", "aphhna", status.HTTP_200_OK, empty_access_list],
        ["user7", "aphhna", status.HTTP_403_FORBIDDEN, empty_access_list],
        ["user8", "aphhna", status.HTTP_200_OK, empty_access_list],
        ["user9", "aphhna", status.HTTP_403_FORBIDDEN, empty_access_list],
        ["user10", "aphhna", status.HTTP_403_FORBIDDEN, empty_access_list],
        *[
            [login, "aphhna", status.HTTP_404_NOT_FOUND, empty_access_list]
            for login in ("user1", "user2", "user3", "user4", "user5", "user6")
        ]
    ]


class TestProjectPermissions(BasePermissionTest):
    """
    Contains test routines for project permissions
    """

    access_level_type = LevelType.project_level

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
        self.assert_permission_list_response(response, expected_status_code, expected_permission_list)

    def get_permission_list_path(self, project_alias):
        """
        Returns the permission path

        :param project_alias: project alias to be used
        :return: full permission path
        """
        return "/api/{version}/projects/{alias}/permissions/".format(version=self.API_VERSION, alias=project_alias)


del BasePermissionTest
