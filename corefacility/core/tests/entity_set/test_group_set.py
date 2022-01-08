from parameterized import parameterized

from core.tests.entity_set.base_test_class import BaseTestClass
from core.tests.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.tests.entity_set.entity_set_objects.user_set_object import UserSetObject


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
        self._user_set_object = TestGroupSet._user_set_object
        self._container = self._group_set_object.clone()
        self.container.sort()

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
