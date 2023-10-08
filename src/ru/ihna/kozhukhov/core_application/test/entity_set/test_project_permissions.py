from parameterized import parameterized

from ... import models
from ...exceptions.entity_exceptions import EntityOperationNotPermitted
from ...entity.entity_sets.access_level_set import AccessLevelSet
from ...entity.entity_sets.project_set import ProjectSet
from ...entity.group import Group
from ...entity.project import Project

from .base_permissions_test import BasePermissionsTest
from ..data_providers.entity_sets import filter_data_provider


def initial_access_level_scheme_provider():
    return [
        (6, 0, "full", None),
        (6, -1, None, None),
        (6, Group(), None, EntityOperationNotPermitted),

        (7, 0, "full", None),
        (7, 1, "data_process", None),
        (7, -1, None, None),
        (7, Group(), None, EntityOperationNotPermitted),

        (8, 0, "data_full", None),
        (8, 1, "full", None),
        (8, 2, "data_view", None),
        (8, -1, None, None),
        (8, Group(), None, EntityOperationNotPermitted),

        (9, 0, "data_add", None),
        (9, 1, "full", None),
        (9, 2, "no_access", None),
        (9, -1, None, None),
        (9, Group(), None, EntityOperationNotPermitted),

        (0, 2, "full", None),
        (0, 3, "data_add", None),
        (0, -1, None, None),
        (0, Group(), None, EntityOperationNotPermitted),

        (1, 2, "full", None),
        (1, 3, "full", None),
        (1, -1, None, None),
        (1, Group(), None, EntityOperationNotPermitted),

        (2, 3, "full", None),
        (2, 4, "data_view", None),
        (2, -1, None, None),
        (2, Group(), None, EntityOperationNotPermitted),

        (3, 3, "data_process", None),
        (3, 4, "full", None),
        (3, -1, None, None),
        (3, Group(), None, EntityOperationNotPermitted),

        (4, 4, "full", None),
        (4, -1, None, None),
        (4, Group(), None, EntityOperationNotPermitted),

        (5, 4, "full", None),
        (5, -1, None, None),
        (5, Group(), None, EntityOperationNotPermitted),

        (Project(), 0, None, EntityOperationNotPermitted),
    ]


def project_index_provider():
    project_list = list(range(10))
    project_list.append(-1)
    return [(project_index,) for project_index in project_list]


def group_set_provider():
    return [
        # project_index     group_index     access_level        state_must_change       is_deletable    is_settable
        (0, 3, "data_add", False, True, True),
        (0, 3, "data_process", False, True, True),
        (0, 2, "no_access", False, False, False),
        (0, -1, "full", True, True, True),
        (0, Group(), "full", False, False, False),

        (1, 2, "data_full", False, True, True),
        (1, 2, "no_access", False, True, True),
        (1, 3, "no_access", False, False, False),
        (1, -1, "data_add", True, True, True),
        (1, Group(), "full", False, False, False),

        (Project(), 0, "full", False, False, False),
    ]


def access_level_provider():
    return [
        (0, [
            (6, False, "full"),
            (7, False, "full,data_process"),
            (8, False, "data_full,full"),
            (9, False, "data_add,full"),
        ]),
        (1, [
            (6, True, "full"),
            (7, True, "full"),
            (8, False, "data_full"),
            (9, False, "data_add"),
        ]),
        (2, [
            (6, False, "full"),
            (7, False, "full,data_process"),
            (8, False, "data_full,full"),
            (9, False, "data_add,full"),
        ]),
        (3, [
            (7, False, "data_process"),
            (8, True, "full,data_view"),
            (9, True, "full,no_access"),
            (0, False, "full"),
            (1, False, "full"),
        ]),
        (4, [
            (7, False, "data_process"),
            (8, False, "full,data_view"),
            (9, False, "full,no_access"),
            (0, True, "full"),
            (1, True, "full"),
        ]),
        (5, [
            (6, False, "full"),
            (7, False, "full"),
            (8, False, "data_full,data_view"),
            (9, False, "data_add,no_access"),
            (0, False, "full,data_add"),
            (1, False, "full,full"),
            (2, False, "full"),
            (3, False, "data_process"),
        ]),
        (6, [
            (8, False, "data_view"),
            (0, False, "full,data_add"),
            (1, False, "full"),
            (2, False, "full,data_view"),
            (3, False, "data_process,full"),
            (4, False, "full"),
            (5, False, "full"),
        ]),
        (7, [
            (0, False, "data_add"),
            (1, True, "full"),
            (2, True, "full,data_view"),
            (3, True, "data_process,full"),
            (4, True, "full"),
            (5, True, "full"),
        ]),
        (8, [
            (0, False, "data_add"),
            (1, False, "full"),
            (2, False, "full,data_view"),
            (3, False, "data_process,full"),
            (4, False, "full"),
            (5, False, "full"),
        ]),
        (9, [
            (2, False, "data_view"),
            (3, False, "full"),
            (4, False, "full"),
            (5, False, "full"),
        ])
    ]


def access_level_slicing_provider():
    return filter_data_provider(
        range(10),
        [
            (slice(3, 7),),
            (slice(0, 10),),
            (slice(10, 20),),
        ]
    )


def access_level_retrieve_provider():
    return filter_data_provider(
        range(10),
        [
            ("id",),
            ("alias",),
        ]
    )


class TestProjectPermission(BasePermissionsTest):
    """
    Tests project permission for the whole project set
    """

    permission_model = models.Permission

    entity_field = "project_id"

    entity_set_class = ProjectSet

    governor_exists = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()
        self.level_set = AccessLevelSet()

    @parameterized.expand(initial_access_level_scheme_provider())
    def test_get_permission(self, project_index, group_index, expected_access_level, expected_exception):
        super().test_get_permission(project_index, group_index, expected_access_level, expected_exception)

    @parameterized.expand(group_set_provider())
    def test_set_permission(self, project_index, group_index, access_level, state_must_change,
                            is_deletable, is_settable):
        super().test_set_permission(project_index, group_index, access_level, state_must_change, is_deletable,
                                    is_settable)
        project = self.get_entity_by_index(project_index)
        if project_index != -1 and group_index == -1:
            self._check_initial_access_scheme(project)

    @parameterized.expand(group_set_provider())
    def test_delete_permission(self, project_index, group_index, access_level, state_must_change,
                               is_deletable, is_settable):
        super().test_delete_permission(project_index, group_index, access_level, state_must_change, is_deletable,
                                       is_settable)
        project = self.get_entity_by_index(project_index)
        if project_index != -1 and group_index == -1:
            self._check_initial_access_scheme(project)

    @parameterized.expand(project_index_provider())
    def test_permission_iteration(self, project_index):
        super().test_permission_iteration(project_index, True)

    @parameterized.expand(project_index_provider())
    def test_permission_one_request_iteration(self, project_index):
        super().test_permission_one_request_iteration(project_index)

    @parameterized.expand(access_level_provider())
    def test_entity_iteration_positive(self, user_index, project_info):
        super().test_entity_iteration_positive(user_index, project_info, True)

    @parameterized.expand(access_level_provider())
    def test_entity_iteration_performance(self, user_index, entity_info):
        super().test_entity_iteration_performance(user_index, entity_info)

    @parameterized.expand(access_level_provider())
    def test_entity_len(self, user_index, entity_info):
        super().test_entity_len(user_index, entity_info)

    @parameterized.expand(access_level_slicing_provider())
    def test_project_slicing(self, user_index, entity_slice):
        user = self.get_user_by_index(user_index)
        project_set = ProjectSet()
        project_set.user = user
        desired_slicing_list = []
        project_index = 0
        for project in project_set:
            if entity_slice.start <= project_index < entity_slice.stop:
                desired_slicing_list.append(project)
            project_index += 1
        with self.assertLessQueries(1):
            actual_slicing_list = project_set[entity_slice]
        self.assertEquals(len(actual_slicing_list), len(desired_slicing_list),
                          msg="Unexpected number of projects in the slice")
        for i in range(len(actual_slicing_list)):
            actual_project = actual_slicing_list[i]
            desired_project = desired_slicing_list[i]
            self.assertEntityEquals(actual_project, desired_project,
                                    "The slicing operation doesn't reveal the same results as iteration "
                                    "for user ID=%d %s %s, project ID=%d %s" %
                                    (user.id, user.surname, user.name, actual_project.id, actual_project.name))
            self.assertEquals(actual_project.is_user_governor, desired_project.is_user_governor,
                              "The slicing doesn't retrieve the user leadership correctly")
            self.assertEquals(actual_project.user_access_level, desired_project.user_access_level,
                              "The slicing operation doesn't reveal the same results as iteration "
                              "for user ID=%d %s %s, project ID=%d %s: The user access level is not the same" %
                              (user.id, user.surname, user.name, actual_project.id, actual_project.name))

    @parameterized.expand(access_level_retrieve_provider())
    def test_entity_retrieve(self, user_index, lookup_field):
        super().test_entity_retrieve(user_index, lookup_field)

    def get_entity_by_index(self, project_index):
        """
        Returns the entity by the index

        :param project_index: the project index
        :return: nothing
        """
        if isinstance(project_index, Project):
            project = project_index
        else:
            project = self._project_set_object[project_index]
        return project

    def get_entity_list(self, project_info):
        return [
            (self._project_set_object[index], is_governor, access_control_list)
            for index, is_governor, access_control_list in project_info
        ]

    def _check_initial_access_scheme(self, project):
        for project_index, group_index, access_level, exception in initial_access_level_scheme_provider():
            another_project = self.get_entity_by_index(project_index)
            if project.id == another_project.id:
                if isinstance(group_index, int) and group_index != -1 and exception is None:
                    group = self.get_group_by_index(group_index)
                    actual_level = project.permissions.get(group)
                    expected_level = AccessLevelSet.project_level(access_level)
                    self.assertAccessLevelEquals(actual_level, expected_level,
                                                 "Changing permissions for one group reflects permission for the "
                                                 "other group")

    def assertEntityEquals(self, actual, expected, msg):
        self.assertEquals(actual.id, expected.id, msg + ". The project IDs are not the same")
        self.assertEquals(actual.state, "loaded", msg + ". The state of the project retrieved is not LOADED")
        self.assertEquals(actual.alias, expected.alias, msg + ". The project alias is not the same")
        self.assertEquals(actual.name, expected.name, msg + ". The project name is not the same")
        self.assertEquals(actual.root_group.id, expected.root_group.id,
                          msg + "The project root group ID is not the same")
        self.assertEquals(actual.root_group.name, expected.root_group.name,
                          msg + "The project root group was not properly retrieved since their name are not the same")
        self.assertEquals(actual.governor.id, expected.governor.id,
                          msg + "The project governor is not the same")
        self.assertEquals(actual.governor.login, expected.governor.login,
                          msg + "The project governor is not  the same, its login was not correctly retrieved")
        self.assertEquals(actual.governor.name, expected.governor.name,
                          msg + "The project governor is not the same, its name was not correctly retrieved")
        self.assertEquals(actual.governor.surname, expected.governor.surname,
                          msg + "The project governor is not the same, its surname was not correctly retrieved")


del BasePermissionsTest
