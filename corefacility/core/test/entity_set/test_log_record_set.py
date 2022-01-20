from parameterized import parameterized

from core.test.data_providers.entity_sets import filter_data_provider

from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.log_set_object import LogSetObject
from .entity_set_objects.log_record_set_object import LogRecordSetObject


def no_filter_data_provider():
    return [
        ("find by ID positive", BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by ID positive", BaseTestClass.TEST_FIND_BY_ID, 1, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by ID positive", BaseTestClass.TEST_FIND_BY_ID, 2, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by ID negative", BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        ("find by alias", BaseTestClass.TEST_FIND_BY_ALIAS, "hello", BaseTestClass.NEGATIVE_TEST_CASE),

        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, 5, BaseTestClass.POSITIVE_TEST_CASE),
        ("find by index", BaseTestClass.TEST_FIND_BY_INDEX, 6, BaseTestClass.NEGATIVE_TEST_CASE),

        ("slicing", BaseTestClass.TEST_SLICING, (1, 5, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (1, 5, 2), BaseTestClass.NEGATIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (1, 5, 0), BaseTestClass.NEGATIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (1, 5, None), BaseTestClass.POSITIVE_TEST_CASE),

        ("slicing", BaseTestClass.TEST_SLICING, (-1, 5, 1), BaseTestClass.NEGATIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (0, 5, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (4, 5, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (5, 5, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (6, 5, 1), BaseTestClass.POSITIVE_TEST_CASE),

        ("slicing", BaseTestClass.TEST_SLICING, (1, 6, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (1, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("slicing", BaseTestClass.TEST_SLICING, (10, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),

        ("iterations", BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        ("counting", BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


def log_filter_provider():
    return filter_data_provider(
        range(5),
        [
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    )


class TestLogRecordSet(BaseTestClass):
    """
    Provides basic testing routines for log record sets
    """

    _user_set_object = None
    _log_set_object = None
    _log_record_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._log_set_object = LogSetObject(cls._user_set_object)
        cls._log_record_set_object = LogRecordSetObject(cls._log_set_object)

    def setUp(self):
        self._user_set_object = self._user_set_object  # calls the __getattribute__ method of the parent class
        self._log_set_object = self._log_set_object  # calls the __getattribute__ method of the parent class
        self._container = self._log_record_set_object.clone()
        self.initialize_filters()

    @parameterized.expand(no_filter_data_provider())
    def test_no_filter(self, test_name, feature_index, arg, test_type):
        with self.assertLessQueries(1):
            self._test_all_access_features(feature_index, arg, test_type)

    @parameterized.expand(log_filter_provider())
    def test_log_filter(self, log_index, *args):
        log = self._log_set_object[log_index]
        self.apply_filter("log", log)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.record_time, expected_entity.record_time,
                          msg + ". Log record times are not the same")
        self.assertEquals(actual_entity.level, expected_entity.level,
                          msg + ". Log levels are not the same")
        self.assertEquals(actual_entity.message, expected_entity.message,
                          msg + ". Log messages are not the same")
        self.assertEquals(actual_entity.log.id, expected_entity.log.id,
                          msg + ". The logs to which this message is attached is not the same")


del BaseTestClass
