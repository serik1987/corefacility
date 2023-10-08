from parameterized import parameterized

from ...entity.entity_sets.group_set import GroupSet
from ...entity.user import User
from ...test.data_providers.entity_sets import filter_data_provider
from ...test.entity_set.base_test_class import BaseTestClass
from ...test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from ...test.entity_set.entity_set_objects.user_set_object import UserSetObject


def initial_conditions_provider():
    return [
        (0, 1, (0, 1, 2)),
        (1, 3, (0, 2, 3, 4)),
        (2, 4, (3, 4, 5, 6)),
        (3, 7, (5, 6, 7, 8)),
        (4, 7, (6, 7, 8, 9)),
    ]


def general_search_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 4, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 5, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (2, 4, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (2, 2, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (2, 1, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (10, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (-1, 4, 1), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (2, 4, 2), BaseTestClass.NEGATIVE_TEST_CASE),
    ]


def base_search_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


def group_name_provider():
    return filter_data_provider(
        ["Сёстры Райт", "Райт", "Управляемый хаос", "Управля", "С", "inexistent", "", None],
        base_search_provider(),
    )


def group_user_provider():
    return filter_data_provider(range(10), base_search_provider())


def group_governor_provider():
    return filter_data_provider(
        (0, 1, 7, None),
        base_search_provider()
    )


class TestGroupSet(BaseTestClass):
    """
    Defines testing routines for group sets
    """

    _user_set_object = None
    _group_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)

    def setUp(self):
        super().setUp()
        self._user_set_object = TestGroupSet._user_set_object
        self._container = self._group_set_object.clone()
        self.container.sort()
        self.initialize_filters()

    @parameterized.expand(initial_conditions_provider())
    def test_initial_conditions(self, group_index, governor_index, member_indices):
        msg = "Initial conditions test failed"
        group = self._group_set_object[group_index]
        self.assertEquals(group.governor, self._user_set_object[governor_index], msg)
        for member_index in member_indices:
            user = self._user_set_object[member_index]
            self.assertTrue(group.users.exists(user), msg)

    @parameterized.expand(general_search_provider())
    def test_general_search(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(group_name_provider())
    def test_group_name(self, search_string, *args):
        self.apply_filter("name", search_string)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(group_user_provider())
    def test_group_user_positive(self, user_index, *args):
        user = self._user_set_object[user_index]
        self.apply_filter("user", user)
        self._test_all_access_features(*args)

    @parameterized.expand(group_user_provider())
    def test_group_user_performance(self, user_index, *args):
        with self.assertLessQueries(2):
            user = self._user_set_object[user_index]
            group_set = GroupSet()
            group_set.user = user
            len1 = len(group_set)
            group_list = [group for group in group_set]
            self.assertEquals(len1, len(group_list), "Group conuting and iteration doesn't give the same item number")

    @parameterized.expand([(True,), (False,)])
    def test_group_user_inexistent(self, create):
        user = User(login="sergei.kozhukhov")
        if create:
            user.create()
        group_set = GroupSet()
        group_set.user = user
        self.assertEquals(len(group_set), 0,
                          "The number of groups are not correct where user is not included in any group")
        for _ in group_set:
            self.fail("When we filter the group set by user not included in any group some groups still found")

    def test_group_user_invalid(self):
        group_set = GroupSet()
        with self.assertRaises(ValueError, msg="The 'user' filter in the group set can have invalid value: 42"):
            group_set.user = 42

    @parameterized.expand(group_governor_provider())
    def test_governor_filter(self, governor_index, *args):
        governor = self._user_set_object[governor_index] if governor_index is not None else None
        self.apply_filter("governor", governor)
        self._test_all_access_features(*args)

    @parameterized.expand(group_governor_provider())
    def test_governor_filter_performance(self, governor_index, *args):
        governor = self._user_set_object[governor_index] if governor_index is not None else None
        with self.assertLessQueries(3):
            group_set = GroupSet()
            group_set.governor = governor
            set_length = len(group_set)
            self.assertEquals(len(group_set[:]), set_length, "Governor filter performance test failed")
            self.assertEquals(len(group_set[5:10]), 0, "The group set contains too much elements")

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        """
        Asserts that the entity has been successfully found.
        Class derivatives can re-implement this method to ensure that all entity fields were uploaded successfully.

        :param actual_entity: the entity found in the database
        :param expected_entity: the entity expected to be found in the database
        :param msg: message to print when the entity is failed to be found
        :return: nothing
        """
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.name, expected_entity.name, msg + ": Group names are not the same")
        self.assertEquals(actual_entity.governor.id, expected_entity.governor.id,
                          msg + ": Governor IDs are not the same")
        self.assertEquals(actual_entity.governor.login, expected_entity.governor.login,
                          msg + ": Governor logins are not the same")
        self.assertEquals(actual_entity.governor.name, expected_entity.governor.name,
                          msg + ": Governor names are not the same")
        self.assertEquals(actual_entity.governor.surname, expected_entity.governor.surname,
                          msg + ": Governor surnames are not the same")
