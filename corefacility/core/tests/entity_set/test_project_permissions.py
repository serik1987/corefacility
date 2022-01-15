from nose_parameterized import parameterized
from parameterized import parameterized_class

from core import models

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.user_set_object import UserSetObject
from ..data_providers.entity_sets import filter_data_provider
from ...entity.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException
from ...entity.entity_sets.access_level_set import AccessLevelSet
from ...entity.entity_sets.project_set import ProjectSet
from ...entity.group import Group
from ...entity.project import Project
from ...entity.user import User
from ...models import ProjectPermission
from ...models.enums import LevelType


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


def access_level_indexation_provider():
    return filter_data_provider(
        range(10),
        [
            (0, None),
            (10, EntityNotFoundException),
        ]
    )


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


@parameterized_class([
    {"default_access_level": "no_access"},
])
class TestProjectPermission(BaseTestClass):
    """
    Tests project permission for the whole project set
    """

    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _sample_group = None

    default_access_level = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls._project_set_object = ProjectSetObject(cls._group_set_object)

    def setUp(self):
        super().setUp()
        self._user_set_object = self.__class__._user_set_object
        self._group_set_object = self.__class__._group_set_object
        self._project_set_object = self.__class__._project_set_object
        self._sample_group = Group(name="Sample group", governor=self._user_set_object[9])
        self._sample_group.create()
        self.change_default_access_level()

    @parameterized.expand(initial_access_level_scheme_provider())
    def test_get_permission(self, project_index, group_index, expected_access_level, expected_exception):
        """
        Checks whether the default project permission was properly set

        :param project_index: the project index within the project set object
        :param group_index: the group index within the group set object, or
            -1 if the group is additionally added or newly created group
        :param expected_access_level: expected access level to set or None if default access level is expected
        :param expected_exception: None for positive test, exception that must be generated for negative test
        :return: nothing
        """
        project = self.get_project_by_index(project_index)
        group = self.get_group_by_index(group_index)
        if expected_access_level is None:
            expected_access_level = self.default_access_level
        if expected_access_level == -1:
            level_set = AccessLevelSet()
            level_set.type = LevelType.app_level
            expected_access_level = level_set.get("add")
        if isinstance(expected_access_level, str):
            level_set = AccessLevelSet()
            level_set.type = LevelType.project_level
            expected_access_level = level_set.get(expected_access_level)
        if expected_exception is not None:
            with self.assertRaises(expected_exception,
                                   msg="Non-permitted access level operation was successfully completed"):
                project.permissions.get(group)
        else:
            actual_access_level = project.permissions.get(group)
            self.assertAccessLevelEquals(actual_access_level, expected_access_level,
                                         "Failed to retrieve proper access level for "
                                         "project name = %s, group name = %s" %
                                         (project.name, group.name))

    @parameterized.expand(group_set_provider())
    def test_set_permission(self, project_index, group_index, access_level, state_must_change,
                            is_deletable, is_settable):
        """
        Checks whether setting additional permissions work correctly

        :param project_index: the project index or newly created project
        :param group_index: the group index or -1 if the group is not within the group object or newly created group
        :param access_level: access level alias
        :param state_must_change: True if number of records in the core_projectpermission table must be changed
        :param is_deletable: True if such a group can be deleted from the access control lists
        :param is_settable: True if permissions for such a group can be modified
        :return: nothing
        """
        project = self.get_project_by_index(project_index)
        group = self.get_group_by_index(group_index)
        desired_access_level = AccessLevelSet.project_level(access_level)
        initial_state = models.ProjectPermission.objects.count()
        if is_settable:
            project.permissions.set(group, desired_access_level)
            final_state = models.ProjectPermission.objects.count()
            if state_must_change:
                self.assertEquals(final_state, initial_state + 1,
                                  "This test case implies adding one extra row to the core_projectpermission table")
            else:
                self.assertEquals(final_state, initial_state,
                                  "The test case doesn't imply adding any extra rows to the "
                                  "core_projectpermission table")
            actual_access_level = project.permissions.get(group)
            self.assertAccessLevelEquals(actual_access_level, desired_access_level,
                                         "The access level was not properly set.")
            if project_index != -1 and group_index == -1:
                self._check_initial_access_scheme(project)
        else:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="The permission was successfully added to the permission list"):
                project.permissions.set(group, access_level)

    @parameterized.expand(group_set_provider())
    def test_delete_permission(self, project_index, group_index, access_level, state_must_change,
                               is_deletable, is_settable):
        """
        Checks whether deleting additional permissions work correctly

        :param project_index: the project index or newly created project
        :param group_index: the group index or -1 if the group is not within the group object or newly created group
        :param access_level: access level alias
        :param state_must_change: True if number of records in the core_projectpermission table must be changed
        :param is_deletable: True if such a group can be deleted from the access control lists
        :param is_settable: True if permissions for such a group can be modified
        :return: nothing
        """
        project = self.get_project_by_index(project_index)
        group = self.get_group_by_index(group_index)
        access_level = AccessLevelSet.project_level(access_level)
        if is_settable:
            project.permissions.set(group, access_level)
        if is_deletable:
            initial_state = models.ProjectPermission.objects.count()
            project.permissions.delete(group)
            final_state = models.ProjectPermission.objects.count()
            self.assertEquals(final_state, initial_state-1,
                              "Deleting project permission didn't result in declining number of rows in the "
                              "core_projectpermission table by 1")
            actual_access_level = project.permissions.get(group)
            desired_access_level = AccessLevelSet.project_level(self.default_access_level)
            self.assertAccessLevelEquals(actual_access_level, desired_access_level,
                                         "The access level for the group doesn't turn to its default state "
                                         "after the delete")
            project.permissions.delete(group)
            dd_state = models.ProjectPermission.objects.count()
            self.assertEquals(dd_state, final_state,
                              "The second project permission delete is not useless")
            if project_index != -1 and group_index == -1:
                self._check_initial_access_scheme(project)
        else:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="The tester is able to violate data consistency: one mandatory permission was "
                                   "successfully deleted"):
                project.permissions.delete(group)

    @parameterized.expand(project_index_provider())
    def test_permission_iteration(self, project_index):
        """
        Checks whether iteration over project permission give the same results as the project's get(...) function

        :param project_index: the project index to reveal
        :return: nothing
        """
        project = self.get_project_by_index(project_index)
        print(project)

    @parameterized.expand(project_index_provider())
    def test_permission_iteration(self, project_index):
        project = self.get_project_by_index(project_index)
        root_group_detected = False
        none_group_detected = False
        permission_count = 0
        for group, actual_access in project.permissions:
            if none_group_detected:
                self.fail("The rest of all permissions doesn't correspond to the last group")
            expected_access = project.permissions.get(group)
            self.assertAccessLevelEquals(actual_access, expected_access,
                                         "The project permission iteration doesn't define the same access levels as "
                                         "Project.permissions.get")
            if group is not None and group.id == project.root_group.id:
                root_group_detected = True
            if not root_group_detected:
                self.fail("The first group in the list is not root group")
            if group is None:
                none_group_detected = True
            permission_count += 1
        expected_permission_count = ProjectPermission.objects \
            .filter(project_id=project.id) \
            .count()
        expected_permission_count += 1  # + 1 root group permission not presented in the database but implied!
        self.assertEquals(permission_count, expected_permission_count,
                          "Number of permissions iterated is not the same as expected")
        self.assertTrue(root_group_detected, "At least one permission must belong to the root group")
        self.assertTrue(none_group_detected, "At least one permission must belong to the rest of the users")

    @parameterized.expand(project_index_provider())
    def test_permission_one_request_iteration(self, project_index):
        with self.assertLessQueries(2):
            project = self.get_project_by_index(project_index)
            for _, _ in project.permissions:
                pass

    @parameterized.expand(access_level_provider())
    def test_project_iteration_positive(self, user_index, project_info):
        user = self.get_user_by_index(user_index)
        project_list = self.get_project_list(project_info)
        project_set = ProjectSet()
        project_set.user = user
        projects_found = set()
        previous_project_name = None
        for project in project_set:
            self.assertFalse(project.id in projects_found, "The project with ID=%d was revealed twice" % project.id)
            desired_project = None
            desired_access_list = None
            desired_governor = None
            for expected_project, is_governor, expected_access_list in project_list:
                if expected_project.id == project.id:
                    desired_project = expected_project
                    desired_access_list = expected_access_list
                    desired_governor = is_governor
                    break
            self.assertIsNotNone(desired_project,
                                 "Some extra project was found: ID=%d %s" % (project.id, project.name))
            self.assertProjectEquals(project, desired_project,
                                     "The project %s was not correctly picked up for user %s" % (project, user))
            if isinstance(desired_access_list, str):
                desired_access_list = set(desired_access_list.split(","))
            if "no_access" in desired_access_list:
                desired_access_list.remove("no_access")
            if len(desired_access_list) == 0:
                self.fail("The project ID=%d %s for user %d %s %s must not be both in actual and "
                          "in the desired access lists according to its access rules" % (project.id, project.name,
                                                                                         user.id, user.surname,
                                                                                         user.name))
            self.assertEquals(project.user_access_level, desired_access_list,
                              "The project access list is wrong for project ID=%d %s, user ID=%d %s %s" %
                              (project.id, project.name, user.id, user.surname, user.name))
            self.assertEquals(project.is_user_governor, desired_governor,
                              "The unexpected governor relation for project ID=%d %s, user ID=%d %s %s" %
                              (project.id, project.name, user.id, user.surname, user.name))
            if previous_project_name is not None:
                self.assertLessEqual(previous_project_name, project.name,
                                     "Unexpected project list ordering for project ID=%d %s, user ID=%d %s %s" %
                                     (project.id, project.name, user.id, user.surname, user.name))
            previous_project_name = project.name
            projects_found.add(project.id)
        self.assertEquals(len(projects_found), len(project_list),
                          "Some of the projects expected were not found for user %d %s %s" %
                          (user.id, user.surname, user.name))

    @parameterized.expand(access_level_provider())
    def test_project_iteration_performance(self, user_index, project_list):
        user = self.get_user_by_index(user_index)
        project_set = ProjectSet()
        project_set.user = user
        with self.assertLessQueries(1):
            for _ in project_set:
                pass

    @parameterized.expand(access_level_provider())
    def test_project_len_performance(self, user_index, project_list):
        user = self.get_user_by_index(user_index)
        project_set = ProjectSet()
        project_set.user = user
        desired_len = 0
        for project in project_set:
            desired_len += 1
        with self.assertLessQueries(1):
            actual_len = len(project_set)
        self.assertEquals(actual_len, desired_len,
                          "Counting projects for user ID=%d %s %s: Iteration and len(....) results are not the same"
                          % (user.id, user.surname, user.name))

    @parameterized.expand(access_level_indexation_provider())
    def test_project_indexation(self, user_index, internal_project_index, throwing_exception):
        user = self.get_user_by_index(user_index)
        project_set = ProjectSet()
        project_set.user = user
        if throwing_exception is None:
            desired_project = None
            for project in project_set:
                desired_project = project
                break
            actual_project = project_set[internal_project_index]
            self.assertProjectEquals(actual_project, desired_project,
                                     "The indexation over project set is not capable to load project correctly")
            self.assertEquals(actual_project.is_user_governor, desired_project.is_user_governor,
                              "The indexation over project set can't define the user governor status correctly")
            self.assertEquals(actual_project.user_access_level, desired_project.user_access_level,
                              "The user access level was not revealed correctly during the project set indexation")
        else:
            with self.assertRaises(throwing_exception,
                                   msg="Successfull revealing the project with incorrect index"):
                actual_project = project_set[internal_project_index]

    @parameterized.expand(access_level_slicing_provider())
    def test_project_slicing(self, user_index, project_slice):
        user = self.get_user_by_index(user_index)
        project_set = ProjectSet()
        project_set.user = user
        desired_slicing_list = []
        project_index = 0
        for project in project_set:
            if project_slice.start <= project_index < project_slice.stop:
                desired_slicing_list.append(project)
            project_index += 1
        with self.assertLessQueries(1):
            actual_slicing_list = project_set[project_slice]
        self.assertEquals(len(actual_slicing_list), len(desired_slicing_list),
                          msg="Unexpected number of projects in the slice")
        for i in range(len(actual_slicing_list)):
            actual_project = actual_slicing_list[i]
            desired_project = desired_slicing_list[i]
            self.assertProjectEquals(actual_project, desired_project,
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
    def test_project_retrieve(self, user_index, lookup_field):
        user = self.get_user_by_index(user_index)
        project_set = ProjectSet()
        project_set.user = user
        for desired_project in project_set:
            with self.assertLessQueries(1):
                actual_project = project_set.get(getattr(desired_project, lookup_field))
            self.assertProjectEquals(actual_project, desired_project,
                                     "Project searching by ID doesn't retrieve the project correctly")
            self.assertEquals(actual_project.is_user_governor, desired_project.is_user_governor,
                              "The project indexation doesn't reveal the user leadership correctly")
            self.assertEquals(actual_project.user_access_level, desired_project.user_access_level,
                              "Project searching by ID doesn't retrieve project permissions correctly")

    def test_project_iteration_negative(self):
        sample_user = self.create_sample_user()
        project_set = ProjectSet()
        project_set.user = sample_user
        for project in project_set:
            self.fail("The project iteration over recently created user revealed the project ID=%d %s" %
                      (project.id, project.name))

    def test_project_count_negative(self):
        sample_user = self.create_sample_user()
        project_set = ProjectSet()
        project_set.user = sample_user
        self.assertEquals(len(project_set), 0,
                          "The project counting over recently created user revealed more than 0 users")

    def test_project_indexation_negative(self):
        sample_user = self.create_sample_user()
        project_set = ProjectSet()
        project_set.user = sample_user
        with self.assertRaises(EntityNotFoundException,
                               msg="The project indexation over recently created user retrieved"
                                   " the project with 0th index"):
            project = project_set[0]

    def change_default_access_level(self):
        default_access_level = AccessLevelSet.project_level(self.default_access_level)
        for project in self._project_set_object:
            project.permissions.set(None, default_access_level)

    def get_project_by_index(self, project_index):
        if isinstance(project_index, Project):
            project = project_index
        else:
            project = self._project_set_object[project_index]
        return project

    def get_group_by_index(self, group_index):
        if isinstance(group_index, Group):
            group = group_index
        elif group_index == -1:
            group = self._sample_group
        else:
            group = self._group_set_object[group_index]
        return group

    def get_user_by_index(self, user_index):
        if isinstance(user_index, User):
            user = user_index
        elif user_index == -1:
            user = User(login="sergei.kozhukhov")
            user.create()
        else:
            user = self._user_set_object[user_index]
        return user

    def get_project_list(self, project_info):
        return [
            (self._project_set_object[index], is_governor, access_control_list)
            for index, is_governor, access_control_list in project_info
        ]

    def create_sample_user(self):
        sample_user = User(login="sergei.kozhukhov")
        sample_user.create()
        return sample_user

    def _check_initial_access_scheme(self, project):
        for project_index, group_index, access_level, exception in initial_access_level_scheme_provider():
            another_project = self.get_project_by_index(project_index)
            if project.id == another_project.id:
                if isinstance(group_index, int) and group_index != -1 and exception is None:
                    group = self.get_group_by_index(group_index)
                    actual_level = project.permissions.get(group)
                    expected_level = AccessLevelSet.project_level(access_level)
                    self.assertAccessLevelEquals(actual_level, expected_level,
                                                 "Changing permissions for one group reflects permission for the "
                                                 "other group")

    def assertAccessLevelEquals(self, actual, expected, msg):
        self.assertEquals(actual.id, expected.id, msg + ". Access level IDs are not the same")
        self.assertEquals(actual.type, expected.type, msg + ". Access level types are not the same")
        self.assertEquals(actual.alias, expected.alias, msg + ". Access level aliases are not the same")
        self.assertEquals(actual.name, expected.name, msg + ". Access level names are not the same")

    def assertProjectEquals(self, actual, expected, msg):
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
