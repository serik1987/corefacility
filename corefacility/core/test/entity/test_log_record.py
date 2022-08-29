from parameterized import parameterized

from core.entity.user import User
from core.entity.log import Log
from core.entity.log_record import LogRecord
from core.entity.entity_exceptions import EntityOperationNotPermitted, EntityFieldInvalid
from core.test.data_providers.field_value_providers import string_provider

from .base_test_class import BaseTestClass
from .entity_objects.log_record_object import LogRecordObject

TEST_NUMBER_ARG = -1


def record_string_provider(min_length, max_length):
    return [
        field_test_args
        for field_test_args in string_provider(min_length, max_length)
        if field_test_args[TEST_NUMBER_ARG] == BaseTestClass.TEST_CREATE_AND_LOAD
    ]


def log_level_provider():
    std_exception_list = (EntityFieldInvalid, ValueError)
    return [
        ("--", "---", std_exception_list),
        ("---", "---", None),
        ("----", "---", std_exception_list),
        ("кас", "---", None),
        ("№№№", "---", None),

    ]


class TestLogRecord(BaseTestClass):
    """
    Provides main test routines for the log record.
    """

    _sample_user = None
    _sample_log = None

    _entity_object_class = LogRecordObject

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._sample_user = User(login="sergei.kozhukhov", name="Sergei", surname="Kozhukhov")
        cls._sample_user.create()

        cls._sample_log = Log(user=cls._sample_user, log_address="/path/to/resource/1/", request_method="GET")
        cls._sample_log.request_date.mark()
        cls._sample_log.create()

        LogRecordObject.define_default_kwarg("log", cls._sample_log)

    def test_object_created_and_deleted(self):
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Some hackers were successfully deleted the log record"):
            super().test_object_created_and_deleted()

    def test_object_created_changed_and_deleted(self):
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Some hackers were successfully deleted the log record"):
            super().test_object_created_changed_and_deleted()

    def test_object_created_loaded_and_deleted(self):
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Some hackers were successfully deleted the log record"):
            super().test_object_created_loaded_and_deleted()

    def test_object_created_plus_updated_default(self):
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Some hackers were successfully changed the log record"):
            super().test_object_created_plus_updated_default()

    def test_object_created_updated_and_loaded_default(self):
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Some hackers were successfully changed the log record"):
            super().test_object_created_updated_and_loaded_default()

    def test_field_log_not_created(self):
        log = Log(user=self._sample_user)
        log.request_date.mark()
        with self.assertRaises((EntityFieldInvalid, ValueError),
                               msg="Inexistent Log has been attached to the log record"):
            record = LogRecord(log=log, message="Sample message", level="DBG")
            record.record_time.mark()
            record.create()

    def test_field_log_invalid(self):
        with self.assertRaises((EntityFieldInvalid, ValueError),
                               msg="Incorrect data type has been used as 'log' value"):
            record = LogRecord(log="hello, world", message="Sample message", level="DBG")
            record.record_time.mark()
            record.create()

    @parameterized.expand(record_string_provider(1, 1024))
    def test_field_message(self, *args):
        self._test_field("message", *args)

    @parameterized.expand(log_level_provider())
    def test_field_level(self, *args):
        self._test_field("level", *args, self.TEST_CREATE_AND_LOAD)

    def _check_default_fields(self, log_record):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param log_record: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(log_record.level, "DBG", "The log level was not successfully transmitted")
        self.assertEquals(log_record.message, "This is my first log record message",
                          "The log message was not successfully transmitted")
        self.assertIsNotNone(log_record.record_time.get(), "The log record time was not set")
        self.assertEquals(log_record.log.id, self._sample_log.id,
                          "The log entity was not successfully transmitted.")

    def _check_default_change(self, log_record):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param log_record: the entity to store
        :return: nothing
        """
        self.assertEquals(log_record.level, "ERR", "Unable to change the log level before its save")
        self.assertEquals(log_record.message, "The message was suddenly editted",
                          "Unable to change the log level before its save")


del BaseTestClass
