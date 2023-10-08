from django.test import TestCase
from parameterized import parameterized

from ...entity.log import Log
from ...exceptions.entity_exceptions import EntityOperationNotPermitted
from ...entity.entity_sets.log_record_set import LogRecordSet


class TestLogHighLevel(TestCase):
    """
    Provides testing of high-level log functions.

    The high-level log functions are simple envelopes of low-level log functions.
    Low-level log functions are standard entity CRUD functions.
    """

    _older_log = None
    _log = None

    def setUp(self):
        super().setUp()
        self._older_log = Log()
        self._older_log.request_date.mark()
        self._older_log.create()

        self._log = Log()
        self._log.request_date.mark()
        self._log.create()

    def test_current_log(self):
        self.assertEquals(Log.current(), self._log,
                          "The Log's current() class function doesn't reveal the same log that has been "
                          "recently created")

    def test_recent_log_changed(self):
        self._log.log_address = "/path/to/some/resource"
        self._log.update()

    def test_previous_log_changed(self):
        self._older_log.log_address = "/path/to/some/resource"
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The log information was suddenly changed"):
            self._older_log.update()

    @parameterized.expand([("DEB", "This is the log record message")])
    def test_add_record(self, level, message):
        Log.current().add_record(level, message)
        record_set = LogRecordSet()
        record = record_set[0]
        self.assertEquals(record.level, level, "The log record level was not transmitted successfully")
        self.assertEquals(record.message, message, "The log record message was not transmitted successfully")
