from rest_framework import status


class ProjectInfo:
    project_alias = None
    access_level = None
    is_user_governor = None

    def __init__(self, project_alias, access_level, is_user_governor):
        self.project_alias = project_alias
        self.access_level = access_level
        self.is_user_governor = is_user_governor


def project_list_provider():
    return [
        (None, status.HTTP_401_UNAUTHORIZED, None),
        ("ordinary_user", status.HTTP_200_OK, []),
        ("superuser", status.HTTP_200_OK, [ProjectInfo(alias, "full", True) for alias in (
            "hhna", "cnl", "mnl", "mn", "nsw", "n", "nl", "gcn", "aphhna", "cr"
        )]),
        ("user1", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", False),
            ProjectInfo("cnl", "full", False),
            ProjectInfo("mnl", "full", False),
            ProjectInfo("mn", "full", False),
        ]),
        ("user2", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", True),
            ProjectInfo("cnl", "full", True),
            ProjectInfo("mnl", "data_full", False),
            ProjectInfo("mn", "data_add", False),
        ]),
        ("user3", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", False),
            ProjectInfo("cnl", "full", False),
            ProjectInfo("mnl", "full", False),
            ProjectInfo("mn", "full", False),
        ]),
        ("user4", status.HTTP_200_OK, [
            ProjectInfo("cnl", "data_process", False),
            ProjectInfo("mnl", "full", True),
            ProjectInfo("mn", "full", True),
            ProjectInfo("nsw", "full", False),
            ProjectInfo("n", "full", False),
        ]),
        ("user5", status.HTTP_200_OK, [
            ProjectInfo("cnl", "data_process", False),
            ProjectInfo("mnl", "full", False),
            ProjectInfo("mn", "full", False),
            ProjectInfo("nsw", "full", True),
            ProjectInfo("n", "full", True),
        ]),
        ("user6", status.HTTP_200_OK, [
            ProjectInfo("hhna", "full", False),
            ProjectInfo("cnl", "full", False),
            ProjectInfo("mnl", "data_full", False),
            ProjectInfo("mn", "data_add", False),
            ProjectInfo("nsw", "full", False),
            ProjectInfo("n", "full", False),
            ProjectInfo("nl", "full", False),
            ProjectInfo("gcn", "data_process", False),
        ]),
        ("user7", status.HTTP_200_OK, [
            ProjectInfo("mnl", "data_view", False),
            ProjectInfo("nsw", "full", False),
            ProjectInfo("n", "full", False),
            ProjectInfo("nl", "full", False),
            ProjectInfo("gcn", "full", False),
            ProjectInfo("aphhna", "full", False),
            ProjectInfo("cr", "full", False),
        ]),
        ("user8", status.HTTP_200_OK, [
            ProjectInfo("nsw", "data_add", False),
            ProjectInfo("n", "full", True),
            ProjectInfo("nl", "full", True),
            ProjectInfo("gcn", "full", True),
            ProjectInfo("aphhna", "full", True),
            ProjectInfo("cr", "full", True),
        ]),
        ("user9", status.HTTP_200_OK, [
            ProjectInfo("nsw", "data_add", False),
            ProjectInfo("n", "full", False),
            ProjectInfo("nl", "full", False),
            ProjectInfo("gcn", "full", False),
            ProjectInfo("aphhna", "full", False),
            ProjectInfo("cr", "full", False),
        ]),
        ("user10", status.HTTP_200_OK, [
            ProjectInfo("nl", "data_view", False),
            ProjectInfo("gcn", "full", False),
            ProjectInfo("aphhna", "full", False),
            ProjectInfo("cr", "full", False),
        ])
    ]


def project_retrieve_provider(status_ok, status_fail):
    def preliminary_data_provider(login):
        return [
            (login, alias, status_fail, None, None)
            for alias in ("nsw", "n", "nl", "gcn", "aphhna", "cr")
        ]
    return [
        ("user1", "hhna", status_ok, "full", False),
        ("user1", "cnl", status_ok, "full", False),
        ("user1", "mnl", status_ok, "full", False),
        ("user1", "mn", status_ok, "full", False),
        *preliminary_data_provider("user1"),

        ("user2", "hhna", status_ok, "full", True),
        ("user2", "cnl", status_ok, "full", True),
        ("user2", "mnl", status_ok, "data_full", False),
        ("user2", "mn", status_ok, "data_add", False),
        *preliminary_data_provider("user2"),

        ("user3", "hhna", status_ok, "full", False),
        ("user3", "cnl", status_ok, "full", False),
        ("user3", "mnl", status_ok, "full", False),
        ("user3", "mn", status_ok, "full", False),
        *preliminary_data_provider("user3"),

        ("user4", "hhna", status_fail, None, None),
        ("user4", "cnl", status_ok, "data_process", False),
        ("user4", "mnl", status_ok, "full", True),
        ("user4", "mn", status_ok, "full", True),
        ("user4", "nsw", status_ok, "full", False),
        ("user4", "n", status_ok, "full", False),
        ("user4", "nl", status_fail, None, None),
        ("user4", "gcn", status_fail, None, None),
        ("user4", "aphhna", status_fail, None, None),
        ("user4", "cr", status_fail, None, None),

        ("user5", "hhna", status_fail, None, None),
        ("user5", "cnl", status_ok, "data_process", False),
        ("user5", "mnl", status_ok, "full", False),
        ("user5", "mn", status_ok, "full", False),
        ("user5", "nsw", status_ok, "full", True),
        ("user5", "n", status_ok, "full", True),
        ("user5", "nl", status_fail, None, None),
        ("user5", "gcn", status_fail, None, None),
        ("user5", "aphhna", status_fail, None, None),
        ("user5", "cr", status_fail, None, None),

        ("user6", "hhna", status_ok, "full", False),
        ("user6", "cnl", status_ok, "full", False),
        ("user6", "mnl", status_ok, "data_full", False),
        ("user6", "mn", status_ok, "data_add", False),
        ("user6", "nsw", status_ok, "full", False),
        ("user6", "n", status_ok, "full", False),
        ("user6", "nl", status_ok, "full", False),
        ("user6", "gcn", status_ok, "data_process", False),
        ("user6", "aphhna", status_fail, None, None),
        ("user6", "cr", status_fail, None, None),

        ("user7", "hhna", status_fail, None, None),
        ("user7", "cnl", status_fail, None, None),
        ("user7", "mnl", status_ok, "data_view", False),
        ("user7", "mn", status_fail, None, None),
        ("user7", "nsw", status_ok, "full", False),
        ("user7", "n", status_ok, "full", False),
        ("user7", "nl", status_ok, "full", False),
        ("user7", "gcn", status_ok, "full", False),
        ("user7", "aphhna", status_ok, "full", False),
        ("user7", "cr", status_ok, "full", False),

        ("user8", "hhna", status_fail, None, None),
        ("user8", "cnl", status_fail, None, None),
        ("user8", "mnl", status_fail, None, None),
        ("user8", "mn", status_fail, None, None),
        ("user8", "nsw", status_ok, "data_add", False),
        ("user8", "n", status_ok, "full", True),
        ("user8", "nl", status_ok, "full", True),
        ("user8", "gcn", status_ok, "full", True),
        ("user8", "aphhna", status_ok, "full", True),
        ("user8", "cr", status_ok, "full", True),

        ("user9", "hhna", status_fail, None, None),
        ("user9", "cnl", status_fail, None, None),
        ("user9", "mnl", status_fail, None, None),
        ("user9", "mn", status_fail, None, None),
        ("user9", "nsw", status_ok, "data_add", False),
        ("user9", "n", status_ok, "full", False),
        ("user9", "nl", status_ok, "full", False),
        ("user9", "gcn", status_ok, "full", False),
        ("user9", "aphhna", status_ok, "full", False),
        ("user9", "cr", status_ok, "full", False),

        ("user10", "hhna", status_fail, None, None),
        ("user10", "cnl", status_fail, None, None),
        ("user10", "mnl", status_fail, None, None),
        ("user10", "mn", status_fail, None, None),
        ("user10", "nsw", status_fail, None, None),
        ("user10", "n", status_fail, None, None),
        ("user10", "nl", status_ok, "data_view", False),
        ("user10", "gcn", status_ok, "full", False),
        ("user10", "aphhna", status_ok, "full", False),
        ("user10", "cr", status_ok, "full", False),
        ("user10", "inexistent", status_fail, None, None),
    ]


def project_write_provider(status_ok, status_fail, status_epic_fail):
    def preliminary_provider(user):
        return [
            (user, project_alias, status_epic_fail)
            for project_alias in ("nsw", "n", "nl", "gcn", "aphhna", "cr")
        ]
    return [
        ("user1", "hhna", status_fail),
        ("user1", "cnl", status_fail),
        ("user1", "mnl", status_fail),
        ("user1", "mn", status_fail),
        *preliminary_provider("user1"),

        ("user2", "hhna", status_ok),
        ("user2", "cnl", status_ok),
        ("user2", "mnl", status_fail),
        ("user2", "mn", status_fail),
        *preliminary_provider("user2"),

        ("user3", "hhna", status_fail),
        ("user3", "cnl", status_fail),
        ("user3", "mnl", status_fail),
        ("user3", "mn", status_fail),
        *preliminary_provider("user3"),

        ("user4", "hhna", status_epic_fail),
        ("user4", "cnl", status_fail),
        ("user4", "mnl", status_ok),
        ("user4", "mn", status_ok),
        ("user4", "nsw", status_fail),
        ("user4", "n", status_fail),
        ("user4", "nl", status_epic_fail),
        ("user4", "gcn", status_epic_fail),
        ("user4", "aphhna", status_epic_fail),
        ("user4", "cr", status_epic_fail),

        ("user5", "hhna", status_epic_fail),
        ("user5", "cnl", status_fail),
        ("user5", "mnl", status_fail),
        ("user5", "mn", status_fail),
        ("user5", "nsw", status_ok),
        ("user5", "n", status_ok),
        ("user5", "nl", status_epic_fail),
        ("user5", "gcn", status_epic_fail),
        ("user5", "aphhna", status_epic_fail),
        ("user5", "cr", status_epic_fail),

        ("user6", "hhna", status_fail),
        ("user6", "cnl", status_fail),
        ("user6", "mnl", status_fail),
        ("user6", "mn", status_fail),
        ("user6", "nsw", status_fail),
        ("user6", "n", status_fail),
        ("user6", "nl", status_fail),
        ("user6", "gcn", status_fail),
        ("user6", "aphhna", status_epic_fail),
        ("user6", "cr", status_epic_fail),

        ("user7", "hhna", status_epic_fail),
        ("user7", "cnl", status_epic_fail),
        ("user7", "mnl", status_fail),
        ("user7", "mn", status_epic_fail),
        ("user7", "nsw", status_fail),
        ("user7", "n", status_fail),
        ("user7", "nl", status_fail),
        ("user7", "gcn", status_fail),
        ("user7", "aphhna", status_fail),
        ("user7", "cr", status_fail),

        ("user8", "hhna", status_epic_fail),
        ("user8", "cnl", status_epic_fail),
        ("user8", "mnl", status_epic_fail),
        ("user8", "mn", status_epic_fail),
        ("user8", "nsw", status_fail),
        ("user8", "n", status_ok),
        ("user8", "nl", status_ok),
        ("user8", "gcn", status_ok),
        ("user8", "aphhna", status_ok),
        ("user8", "cr", status_ok),

        ("user9", "hhna", status_epic_fail),
        ("user9", "cnl", status_epic_fail),
        ("user9", "mnl", status_epic_fail),
        ("user9", "mn", status_epic_fail),
        ("user9", "nsw", status_fail),
        ("user9", "n", status_fail),
        ("user9", "nl", status_fail),
        ("user9", "gcn", status_fail),
        ("user9", "aphhna", status_fail),
        ("user9", "cr", status_fail),

        ("user10", "hhna", status_epic_fail),
        ("user10", "cnl", status_epic_fail),
        ("user10", "mnl", status_epic_fail),
        ("user10", "mn", status_epic_fail),
        ("user10", "nsw", status_epic_fail),
        ("user10", "n", status_epic_fail),
        ("user10", "nl", status_fail),
        ("user10", "gcn", status_fail),
        ("user10", "aphhna", status_fail),
        ("user10", "cr", status_fail),
        ("user10", "inexistent", status_epic_fail),
    ]


def project_update_provider():
    return [
        (update_method, *args)
        for update_method in ("put", "patch")
        for args in project_write_provider(status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
    ]


def project_search_provider():
    return [
        (search_substring, profile_name)
        for search_substring in ("Нейроонтогенез", "Нейро", "", None, "Название несуществующего проекта")
        for profile_name in ("basic", "light")
    ]