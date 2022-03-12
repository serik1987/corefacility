from datetime import timedelta
import platform

from parameterized import parameterized

from core.entity.entity_sets.log_set import LogSet
from core.test.data_providers.entity_sets import filter_data_provider

from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.log_set_object import LogSetObject


def no_filter_provider():
    return [
        ("find by id", BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by id", BaseTestClass.TEST_FIND_BY_ID, 31, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by id", BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, 31, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, 32, BaseTestClass.NEGATIVE_TEST_CASE),

        ("slicing", BaseTestClass.TEST_SLICING, (10, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 20, 2), BaseTestClass.NEGATIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 20, 0), BaseTestClass.NEGATIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 9, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 10, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 11, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 31, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 32, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, None, None), BaseTestClass.NEGATIVE_TEST_CASE),

        ("slicing", BaseTestClass.TEST_SLICING, (-1, 20, None), BaseTestClass.NEGATIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (0, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (1, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (19, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (20, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (21, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (None, 20, None), BaseTestClass.POSITIVE_TEST_CASE),

        ("slicing", BaseTestClass.TEST_SLICING, (None, None, None), BaseTestClass.POSITIVE_TEST_CASE),

        ("iteration", BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ("count", BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


def ip_address_provider():
    ips = ["127.0.0.1", "2001:db8:0:0:1::1", "::1", "8.8.8.8"]
    value_provider = [
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]
    return filter_data_provider(ips, value_provider)


def user_filter_provider():
    return filter_data_provider(range(6), [
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ])


class TestLogSet(BaseTestClass):
    """
    Tests the log set and useful log retrieve.
    """

    _user_set_object = None
    _log_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._log_set_object = LogSetObject(cls._user_set_object)

    def setUp(self):
        super().setUp()
        self._user_set_object = self._user_set_object
        self._container = self._log_set_object.clone()
        self.container.sort()
        self.initialize_filters()

    @parameterized.expand(no_filter_provider())
    def test_no_filter(self, comment, feature_index, arg, test_type):
        with self.assertLessQueries(1):
            self._test_all_access_features(feature_index, arg, test_type)

    @parameterized.expand([
        (cnt, action)
        for cnt in (10, 20, 30)
        for action in ("count", "iter")
    ])
    def test_request_date_from(self, cnt, action):
        if platform.system().lower() == "windows":
            return
        log_set = LogSet()
        filter_date = log_set[cnt].request_date.get() - timedelta(milliseconds=1)
        self.apply_filter("request_date_from", filter_date)
        with self.assertLessQueries(1):
            if action == "count":
                self._test_all_access_features(self.TEST_COUNT, None, self.POSITIVE_TEST_CASE)
            if action == "iter":
                self._test_all_access_features(self.TEST_ITERATION, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand([
        (cnt, action)
        for cnt in (10, 20, 30)
        for action in ("count", "iter")
    ])
    def test_request_date_to(self, cnt, action):
        if platform.system().lower() == "windows":
            return
        log_set = LogSet()
        filter_date = log_set[cnt].request_date.get() + timedelta(milliseconds=1)
        self.apply_filter("request_date_to", filter_date)
        with self.assertLessQueries(1):
            if action == "count":
                self._test_all_access_features(self.TEST_COUNT, None, self.POSITIVE_TEST_CASE)
            if action == "iter":
                self._test_all_access_features(self.TEST_ITERATION, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand(ip_address_provider())
    def test_ip_filter(self, ip_address, *actions):
        self.apply_filter("ip_address", ip_address)
        with self.assertLessQueries(1):
            self._test_all_access_features(*actions)

    @parameterized.expand(user_filter_provider())
    def test_user_filter(self, user_index, *args):
        user = self._user_set_object[user_index]
        self.apply_filter("user", user)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        if platform.system().lower() == "windows":
            return
        self.assertEquals(actual_entity.request_date, expected_entity.request_date,
                          msg + ". Request dates are not the same")
        self.assertLinesEqual(actual_entity.log_address, expected_entity.log_address,
                              msg + ". Log addresses are not the same")
        self.assertLinesEqual(actual_entity.request_method, expected_entity.request_method,
                              msg + ". The request method is not the same")
        self.assertEquals(actual_entity.ip_address, expected_entity.ip_address,
                          msg + ". IP addresses are not the same")
        if actual_entity.user is None:
            self.assertIsNone(expected_entity.user, msg + ". Users are not the same")
        else:
            self.assertEquals(actual_entity.user.id, expected_entity.user.id, msg + ". User IDs not the same")
            self.assertEquals(actual_entity.user.login, expected_entity.user.login, msg + ". Logins are not the same")
            self.assertEquals(actual_entity.user.name, expected_entity.user.name,
                              msg + ". User's names are not the same")
            self.assertEquals(actual_entity.user.surname, expected_entity.user.surname,
                              msg + ". User's surnames are not the same")

    def assertLinesEqual(self, line1, line2, msg):
        if line1 is None:
            line1 = ''
        if line2 is None:
            line2 = ''
        self.assertEquals(line1, line2, msg)


del BaseTestClass
