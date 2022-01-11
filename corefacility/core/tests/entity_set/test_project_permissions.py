from nose_parameterized import parameterized
from parameterized import parameterized_class

from core import models

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.user_set_object import UserSetObject
from ...entity.entity_exceptions import EntityOperationNotPermitted
from ...entity.entity_sets.access_level_set import AccessLevelSet
from ...entity.group import Group
from ...entity.project import Project
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

        (1, 2, "data_full", None),
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
        self._user_set_object = self.__class__._user_set_object
        self._group_set_object = self.__class__._group_set_object
        self._project_set_object = self.__class__._project_set_object
        self._sample_group = Group(name="Sample group", governor=self._user_set_object[9])
        self._sample_group.create()

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
