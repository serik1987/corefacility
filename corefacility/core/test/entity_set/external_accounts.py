from parameterized import parameterized

from core.entity.user import User

from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from ..data_providers.entity_sets import filter_data_provider


def no_filter_provider():
    return [
        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 4, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ALIAS, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, 1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "", BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 4, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 5, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE)
    ]


def user_filter_provider():
    user_set_positive = [0, 2, 4, 6, 8]
    user_set_negative = [1, 3, 5, 7, 9, User(login="sample")]

    test_case_positive = [
        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]

    test_case_negative = [
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]

    return filter_data_provider(user_set_positive, test_case_positive) + \
        filter_data_provider(user_set_negative, test_case_negative)


class TestExternalAccounts(BaseTestClass):
    """
    Provides common test facilities for the base test class
    """

    _external_account_set_object_class = None
    """ To apply these tests first, create the account set object, next, put its names here. """

    _user_set_object = None
    _account_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._account_set_object = cls._external_account_set_object_class(cls._user_set_object)
        print(cls._user_set_object)

    def setUp(self):
        super().setUp()
        self._user_set_object = self._user_set_object
        self._container = self._account_set_object.clone()
        self.initialize_filters()

    def test_account_number(self):
        self.assertEquals(len(self.container), 5,
                          "Some tests will be inherited from the base class. They will work if and only "
                          "if the container contains exactly five object")

    @parameterized.expand(no_filter_provider())
    def test_no_filter(self, number, arg, test_type):
        if number == self.TEST_FIND_BY_ALIAS and type(arg) == int:
            arg = self._no_filter_accounts[arg]
        with self.assertLessQueries(1):
            self._test_all_access_features(number, arg, test_type)

    @parameterized.expand(user_filter_provider())
    def test_user_filter(self, user, number, arg, test_type):
        """
        Tests the user filter property
        """
        if isinstance(user, int):
            user = self._user_set_object[user]
        self.apply_filter("user", user)
        with self.assertLessQueries(1):
            self._test_all_access_features(number, arg, test_type)

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.user.id, expected_entity.user.id,
                          msg="The user ID is not the same as expected")
        self.assertEquals(actual_entity.user.login, expected_entity.user.login,
                          msg="The user login is not the same as expected")
        self.assertEquals(actual_entity.user.name, expected_entity.user.name,
                          msg="The user name is not the same as expected")
        self.assertEquals(actual_entity.user.surname, expected_entity.user.surname,
                          msg="The user surname is not the same as expected")


del BaseTestClass
