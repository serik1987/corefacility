import warnings

from parameterized import parameterized

from core.models import User as UserModel
from core.entity.entity_sets.user_set import UserSet

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.user_set_object import UserSetObject
from ..data_providers.entity_sets import filter_data_provider
from ..data_providers.field_value_providers import image_provider
from ...entity.group import Group
from ...entity.user import User


def general_test_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 9, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 10, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ALIAS, "user3", BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "user20", BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "", BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "Полина", BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 9, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 10, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (3, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (-1, 7, 1), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (0, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (6, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (7, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 3, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 4, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 10, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 11, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (9, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (10, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),
    ]


def short_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


def name_provider():
    return filter_data_provider(
        ["Иванов", "Миронова", "ов", "Сергей", "Полина", "user1", "user10", "support", "xxx", "", None],
        short_provider()
    )


def is_locked_provider():
    return filter_data_provider(
        [(True, (0, 3, 5, 8)), (False, (0, 3, 5, 8))],
        short_provider(),
    )


def group_index_provider():
    return filter_data_provider(
        range(5),
        short_provider()
    )


class TestUserSet(BaseTestClass):
    """
    Tests the user set
    """

    __user_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.__user_set_object = UserSetObject()
        files = list(filter(lambda info: info[2] == 0, image_provider()))
        cls.load_random_avatars(cls.__user_set_object, (0, 2, 5), "avatar", files)

    def setUp(self):
        super().setUp()
        self._container = self.__user_set_object.clone()
        self._container.sort()
        self.initialize_filters()
        self.apply_filter("is_support", False)

    def test_environment_valid(self):
        user_set = UserSet()
        self.assertEquals(len(self._container), 10, "The number of test users created by the user set object is wrong")
        self.assertEquals(len(user_set), 11, "Total number of users stored in the database is not valid")
        pass

    def test_find_support(self):
        user_set = UserSet()
        user = user_set.get("support")
        sample_user = User(_src=self.container,
                           id=user.id,
                           login="support",
                           is_superuser=True,
                           is_support=True,
                           )
        self.assertEntityFound(user, sample_user, msg="The support user is not properly loaded")
        pass

    @parameterized.expand(general_test_provider())
    def test_general_features(self, *args):
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(name_provider())
    def test_find_by_name(self, name, *args):
        self.apply_filter("name", name)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    @parameterized.expand(group_index_provider())
    def test_find_by_group(self, group_index, *args):
        group_set_object = GroupSetObject(self.container.clone())
        self.apply_filter("group", group_set_object[group_index])
        self._test_all_access_features(*args)

    @parameterized.expand(is_locked_provider())
    def test_is_locked(self, is_locked, locked_indices, *args):
        for i in locked_indices:
            user = self.__user_set_object[i]
            user.is_locked = True
            user.update()
        self.apply_filter("is_locked", is_locked)
        self._test_all_access_features(*args)

    def assertEntityFound(self, actual_user, expected_user, msg):
        """
        Asserts that the entity has been successfully found.
        Class derivatives can re-implement this method to ensure that all entity fields were uploaded successfully.

        :param actual_user: the entity found in the database
        :param expected_user: the entity expected to be found in the database
        :param msg: message to print when the entity is failed to be found
        :return: nothing
        """
        super().assertEntityFound(actual_user, expected_user, msg)
        self.assertEquals(actual_user.login, expected_user.login, "Logins are not the same")
        self.assertEquals(actual_user.name, expected_user.name, "First names are not the same")
        self.assertEquals(actual_user.surname, expected_user.surname, "Last names are not the same")
        self.assertEquals(actual_user.email, expected_user.email, "User e-mails are not the same")
        self.assertEquals(actual_user.phone, expected_user.phone, "User phone numbers are not the same")
        self.assertEquals(actual_user.is_locked, expected_user.is_locked, "User lock status are not the same")
        self.assertEquals(actual_user.is_superuser, expected_user.is_superuser, "Superuser status is not the same")
        self.assertEquals(actual_user.is_support, expected_user.is_support, "The support status is not the same")
        self.assertEquals(actual_user.avatar.url, expected_user.avatar.url, "User avatar URLs are not the same")


del BaseTestClass
