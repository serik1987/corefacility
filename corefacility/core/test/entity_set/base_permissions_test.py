from parameterized import parameterized

from core.entity.user import User
from core.entity.group import Group
from core.entity.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException

from core.test.data_providers.entity_sets import filter_data_provider
from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject


def access_level_indexation_provider():
    return filter_data_provider(
        range(10),
        [
            (0, None),
            (10, EntityNotFoundException),
        ]
    )


class BasePermissionsTest(BaseTestClass):
    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _sample_group = None

    default_access_level = "no_access"
    level_set = None
    permission_model = None
    entity_field = None
    entity_set_class = None
    entity_id_field = "id"
    governor_exists = False

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

    def test_get_permission(self, entity_index, group_index, expected_access_level, expected_exception):
        """
        Checks whether the default project permission was properly set

        :param entity_index: the index of the entity within the entity set
        :param group_index: the group index within the group set object, or
            -1 if the group is additionally added or newly created group
        :param expected_access_level: expected access level to set or None if default access level is expected
        :param expected_exception: None for positive test, exception that must be generated for negative test
        :return: nothing
        """
        entity = self.get_entity_by_index(entity_index)
        group = self.get_group_by_index(group_index)
        if expected_access_level is None:
            expected_access_level = self.default_access_level
        if expected_access_level == -1:
            expected_access_level = self.get_incorrect_access_level()
        if isinstance(expected_access_level, str):
            expected_access_level = self.level_set.get(expected_access_level)
        if expected_exception is not None:
            with self.assertRaises(expected_exception,
                                   msg="Non-permitted access level operation was successfully completed"):
                entity.permissions.get(group)
        else:
            actual_access_level = entity.permissions.get(group)
            self.assertAccessLevelEquals(actual_access_level, expected_access_level,
                                         "Failed to retrieve proper access level for "
                                         "project name = %s, group name = %s" %
                                         (entity.name, group.name))

    def test_set_permission(self, entity_index, group_index, access_level, state_must_change,
                            is_deletable, is_settable):
        """
        Checks whether setting additional permissions work correctly

        :param entity_index: the project index or newly created project
        :param group_index: the group index or -1 if the group is not within the group object or newly created group
        :param access_level: access level alias
        :param state_must_change: True if number of records in the core_projectpermission table must be changed
        :param is_deletable: True if such a group can be deleted from the access control lists
        :param is_settable: True if permissions for such a group can be modified
        :return: nothing
        """
        entity = self.get_entity_by_index(entity_index)
        group = self.get_group_by_index(group_index)
        desired_access_level = self.level_set.get(access_level)
        initial_state = self.permission_model.objects.count()
        if is_settable:
            entity.permissions.set(group, desired_access_level)
            final_state = self.permission_model.objects.count()
            if state_must_change:
                self.assertEquals(final_state, initial_state + 1,
                                  "This test case implies adding one extra row to the core_projectpermission table")
            else:
                self.assertEquals(final_state, initial_state,
                                  "The test case doesn't imply adding any extra rows to the "
                                  "core_projectpermission table")
            actual_access_level = entity.permissions.get(group)
            self.assertAccessLevelEquals(actual_access_level, desired_access_level,
                                         "The access level was not properly set.")
        else:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="The permission was successfully added to the permission list"):
                entity.permissions.set(group, access_level)

    def test_delete_permission(self, entity_index, group_index, access_level, state_must_change,
                               is_deletable, is_settable):
        """
        Checks whether deleting additional permissions work correctly

        :param entity_index: the project index or newly created project
        :param group_index: the group index or -1 if the group is not within the group object or newly created group
        :param access_level: access level alias
        :param state_must_change: True if number of records in the core_projectpermission table must be changed
        :param is_deletable: True if such a group can be deleted from the access control lists
        :param is_settable: True if permissions for such a group can be modified
        :return: nothing
        """
        entity = self.get_entity_by_index(entity_index)
        group = self.get_group_by_index(group_index)
        access_level = self.level_set.get(access_level)
        if is_settable:
            entity.permissions.set(group, access_level)
        if is_deletable:
            initial_state = self.permission_model.objects.count()
            entity.permissions.delete(group)
            final_state = self.permission_model.objects.count()
            self.assertEquals(final_state, initial_state - 1,
                              "Deleting project permission didn't result in declining number of rows in the "
                              "core_projectpermission table by 1")
            actual_access_level = entity.permissions.get(group)
            desired_access_level = self.level_set.get(self.default_access_level)
            self.assertAccessLevelEquals(actual_access_level, desired_access_level,
                                         "The access level for the group doesn't turn to its default state "
                                         "after the delete")
            entity.permissions.delete(group)
            dd_state = self.permission_model.objects.count()
            self.assertEquals(dd_state, final_state,
                              "The second project permission delete is not useless")
        else:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="The tester is able to violate data consistency: one mandatory permission was "
                                   "successfully deleted"):
                entity.permissions.delete(group)

    def test_permission_iteration(self, entity_index, root_group_exists):
        """
        Tests how iteration over permissions is organized

        :param entity_index: index of an entity within the entity set
        :param root_group_exists: True is there is root group for certain entity which belonging shall be checked
            False if no root group is implied
        :return: nothing
        """
        entity = self.get_entity_by_index(entity_index)
        root_group_detected = False
        none_group_detected = False
        permission_count = 0
        for group, actual_access in entity.permissions:
            if none_group_detected:
                self.fail("The rest of all permissions doesn't correspond to the last group")
            expected_access = entity.permissions.get(group)
            self.assertAccessLevelEquals(actual_access, expected_access,
                                         "The project permission iteration doesn't define the same access levels as "
                                         "Project.permissions.get")
            if group is not None and root_group_exists and group.id == entity.root_group.id:
                root_group_detected = True
                if not root_group_detected:
                    self.fail("The first group in the list is not root group")
            if group is None:
                none_group_detected = True
            permission_count += 1
        expected_permission_count = self.permission_model.objects \
            .filter(**{self.entity_field: entity.id}) \
            .count()
        expected_permission_count += 1  # + 1 root group permission not presented in the database but implied!
        self.assertEquals(permission_count, expected_permission_count,
                          "Number of permissions iterated is not the same as expected")
        if root_group_exists:
            self.assertTrue(root_group_detected, "At least one permission must belong to the root group")
        self.assertTrue(none_group_detected, "At least one permission must belong to the rest of the users")

    def test_permission_one_request_iteration(self, entity_index):
        """
        Checks whether all permissions could be iterated in one request

        :param entity_index: the entity index
        :return: nothing
        """
        with self.assertLessQueries(2):
            entity = self.get_entity_by_index(entity_index)
            for _, _ in entity.permissions:
                pass

    def test_entity_iteration_positive(self, user_index, entity_info, governor_exists):
        """
        Checks whether the iteration over entity could be done in one request.

        :param user_index: index within the user set
        :param entity_info: information about the project -> array of (project index, whether the user is governor,
        access control list)
        :param governor_exists: whether 'governor' property exists for such an entity
        :return: nothing
        """
        user = self.get_user_by_index(user_index)
        entity_list = self.get_entity_list(entity_info)
        entity_set = self.entity_set_class()
        entity_set.user = user
        entities_found = set()
        previous_entity_name = None
        for entity in entity_set:
            entity_id = getattr(entity, self.entity_id_field)
            self.assertFalse(entity_id in entities_found, "The project with ID=%s was revealed twice" % entity_id)
            desired_entity = None
            desired_access_list = None
            desired_governor = None
            for expected_entity, is_governor, expected_access_list in entity_list:
                expected_entity_id = getattr(expected_entity, self.entity_id_field)
                if entity_id == expected_entity_id:
                    desired_entity = expected_entity
                    desired_access_list = expected_access_list
                    desired_governor = is_governor
            self.assertIsNotNone(desired_entity,
                                 "Some extra entity was found: ID=%s %s" % (entity_id, entity.name))
            self.assertEntityEquals(entity, desired_entity,
                                    "The entity %s was not correctly picked up for user %s" % (entity, user))
            if isinstance(desired_access_list, str):
                desired_access_list = set(desired_access_list.split(","))
            if "no_access" in desired_access_list:
                desired_access_list.remove("no_access")
            if len(desired_access_list) == 0:
                self.fail("The entity ID=%s %s for user %d %s %s must not be both in actual and "
                          "in the desired access lists according to its access rules" % (entity_id, entity.name,
                                                                                         user.id, user.surname,
                                                                                         user.name))
            self.assertEquals(entity.user_access_level, desired_access_list,
                              "The entity access list is wrong for project ID=%s %s, user ID=%d %s %s" %
                              (entity_id, entity.name, user.id, user.surname, user.name))
            if governor_exists:
                self.assertEquals(entity.is_user_governor, desired_governor,
                                  "The unexpected governor relation for project ID=%s %s, user ID=%d %s %s" %
                                  (entity.id, entity.name, user.id, user.surname, user.name))
            if previous_entity_name is not None:
                self.assertLessEqual(previous_entity_name, entity.name,
                                     "Unexpected project list ordering for project ID=%s %s, user ID=%d %s %s" %
                                     (entity.id, entity.name, user.id, user.surname, user.name))
            previous_entity_name = entity.name
            entities_found.add(entity_id)
        self.assertEquals(len(entities_found), len(entity_list),
                          "Some of the projects expected were not found for user %d %s %s" %
                          (user.id, user.surname, user.name))

    def test_entity_iteration_performance(self, user_index, entity_info):
        user = self.get_user_by_index(user_index)
        entity_set = self.entity_set_class()
        entity_set.user = user
        with self.assertLessQueries(1):
            for _ in entity_set:
                pass

    def test_entity_len(self, user_index, entity_info):
        user = self.get_user_by_index(user_index)
        entity_set = self.entity_set_class()
        entity_set.user = user
        desired_len = 0
        for project in entity_set:
            desired_len += 1
        with self.assertLessQueries(1):
            actual_len = len(entity_set)
        self.assertEquals(actual_len, desired_len,
                          "Counting projects for user ID=%d %s %s: Iteration and len(....) results are not the same"
                          % (user.id, user.surname, user.name))

    @parameterized.expand(access_level_indexation_provider())
    def test_entity_indexation(self, user_index, internal_entity_index, throwing_exception):
        user = self.get_user_by_index(user_index)
        entity_set = self.entity_set_class()
        entity_set.user = user
        if throwing_exception is None:
            desired_entity = None
            for entity in entity_set:
                desired_entity = entity
                break
            actual_entity = entity_set[internal_entity_index]
            self.assertEntityEquals(actual_entity, desired_entity,
                                    "The indexation over project set is not capable to load project correctly")
            if self.governor_exists:
                self.assertEquals(actual_entity.is_user_governor, desired_entity.is_user_governor,
                                  "The indexation over project set can't define the user governor status correctly")
            self.assertEquals(actual_entity.user_access_level, desired_entity.user_access_level,
                              "The user access level was not revealed correctly during the project set indexation")
        else:
            with self.assertRaises(throwing_exception,
                                   msg="Successfull revealing the project with incorrect index"):
                actual_project = entity_set[internal_entity_index]

    def test_entity_retrieve(self, user_index, lookup_field):
        user = self.get_user_by_index(user_index)
        entity_set = self.entity_set_class()
        entity_set.user = user
        for desired_entity in entity_set:
            with self.assertLessQueries(1):
                actual_project = entity_set.get(getattr(desired_entity, lookup_field))
            self.assertEntityEquals(actual_project, desired_entity,
                                    "Project searching by ID doesn't retrieve the project correctly")
            if self.governor_exists:
                self.assertEquals(actual_project.is_user_governor, desired_entity.is_user_governor,
                                  "The project indexation doesn't reveal the user leadership correctly")
            self.assertEquals(actual_project.user_access_level, desired_entity.user_access_level,
                              "Project searching by ID doesn't retrieve project permissions correctly")

    def test_entity_iteration_negative(self):
        sample_user = self.create_sample_user()
        entity_set = self.entity_set_class()
        entity_set.user = sample_user
        for entity in entity_set:
            self.fail("The project iteration over recently created user revealed the project ID=%d %s" %
                      (entity.id, entity.name))

    def test_entity_count_negative(self):
        sample_user = self.create_sample_user()
        entity_set = self.entity_set_class()
        entity_set.user = sample_user
        self.assertEquals(len(entity_set), 0,
                          "The project counting over recently created user revealed more than 0 users")

    def test_project_indexation_negative(self):
        sample_user = self.create_sample_user()
        entity_set = self.entity_set_class()
        entity_set.user = sample_user
        with self.assertRaises(EntityNotFoundException,
                               msg="The project indexation over recently created user retrieved"
                                   " the project with 0th index"):
            project = entity_set[0]

    def get_entity_by_index(self, entity_index):
        """
        Returns the entity by the index

        :param entity_index: index of the entity within the entity set
        :return: the entity itself
        """
        raise NotImplementedError("Please, implement the get_entity_by_index")

    def get_incorrect_access_level(self):
        """
        Returns the access level that can't be set in any way

        :return: an AccessLevel entity
        """
        raise NotImplementedError("Please, implement the get_incorrect_access_level")

    def get_group_by_index(self, group_index):
        if isinstance(group_index, Group):
            group = group_index
        elif group_index == -1:
            group = self._sample_group
        else:
            group = self._group_set_object[group_index]
        return group

    def get_user_by_index(self, user_index):
        """
        Finds the user in the user set which index corresponds to a given value

        :param user_index:
        :return:
        """
        if isinstance(user_index, User):
            user = user_index
        elif user_index == -1:
            user = User(login="sergei.kozhukhov")
            user.create()
        else:
            user = self._user_set_object[user_index]
        return user

    def get_entity_list(self, entity_info):
        """
        Restores the entity list by project info

        :param entity_info: list of (entity_index, is_governor, access_control_list)
        :return: the project list of (entity, is_governor, access_control_list
        """
        raise NotImplementedError("get_entity_list is not defined")

    def create_sample_user(self):
        sample_user = User(login="sergei.kozhukhov")
        sample_user.create()
        return sample_user

    def assertAccessLevelEquals(self, actual, expected, msg):
        """
        Checks whether two access levels were equal to each other

        :param actual: an actual access level
        :param expected: access level to be expected
        :param msg: message to show
        :return: nothing
        """
        self.assertEquals(actual.id, expected.id, msg + ". Access level IDs are not the same")
        self.assertEquals(actual.type, expected.type, msg + ". Access level types are not the same")
        self.assertEquals(actual.alias, expected.alias, msg + ". Access level aliases are not the same")
        self.assertEquals(actual.name, expected.name, msg + ". Access level names are not the same")

    def assertEntityEquals(self, actual, expected, msg):
        """
        Asserts that two entities were the same to each other

        :param actual: first entity
        :param expected: second entity
        :param msg: message to show if two entities were not equal to each other
        :return: nothing
        """
        raise NotImplementedError("assertEntityEquals was not implemented")


del BaseTestClass
