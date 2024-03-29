import logging
from datetime import datetime

from django.test import TestCase
from django.test import client
from django.utils.timezone import make_aware
from parameterized import parameterized

from ...entity.entity_sets.log_set import LogSet
from ...entity.entity_sets.log_record_set import LogRecordSet
from ...test.sample_log_mixin import log_provider, SampleLogMixin


class TestLogBase(SampleLogMixin, TestCase):
    """
    Provides the base testing facility for the log system.
    """

    TEST_RECORDS = [
        {"level": "CRI", "message": "This is a critical test message"},
        {"level": "ERR", "message": "This is an error test message"},
        {"level": "WAR", "message": "This is a warning test message"},
        {"level": "INF", "message": "This is an info test message"},
    ]

    __client = None
    __log_set = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()
        self.__client = client.Client(raise_request_exception=False)
        self.__log_set = LogSet()
        self.__record_set = LogRecordSet()
        logger = logging.getLogger("django.request")
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL)

    def tearDown(self):
        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_level)
        super().tearDown()

    @parameterized.expand(log_provider())
    def test_base(self, debug_mode, interface, method, data_index, response_type):
        """
        Provides the base testing features
        :param debug_mode: Forces certain debug mode (either True or False)
        :param interface: either 'ui' for testing the UI interface or 'api' for testing the API interface
        :param method: the request method
        :param data_index: either 0 or 1 depending on corresponding data
        :param response_type: HTTP response code (200, 400, 403, 404, 500)
        """
        with self.settings(DEBUG=debug_mode):
            request_path = self.REQUEST_PATH.format(interface=interface, power=self.ALL_POWERS[data_index])
            response = self.make_test_request(self.__client, interface, method, data_index, response_type)
            self.assertEquals(response.status_code, response_type,
                              "There is an internal error in the testing request: %s" % str(response.exc_info))
            log_number = len(self.__log_set)
            if method.lower() in ["get", "head"] and not debug_mode:
                self.assertEquals(log_number, 0, "All GET request shall not be written when debug mode is off")
            else:
                self.assertEquals(log_number, 1, "This request must be logged")
                log = self.__log_set[0]
                ct = make_aware(datetime.now())
                if not (log.request_date.get() <= ct):
                    print(log.request_date.get(), ct)
                self.assertLessEqual(log.request_date.get(), ct, "The request date must be less than current date")
                self.assertEquals(log.log_address, request_path.split("?")[0],
                                  "The request path must be stored correctly")
                self.assertEquals(log.request_method.lower(), method.lower(),
                                  "The request method must be stored correctly")
                self.assertEquals(str(log.ip_address), "127.0.0.1",
                                  "The IP address must be 127.0.0.1")
                self.assertEquals(log.response_status, response.status_code,
                                  "The response status must be written correctly")

    def test_no_log_record(self):
        self.__client.get("/__test__/logger/")
        self.assertEquals(len(self.__log_set), 0, "The log must not be recorded")
        self.assertEquals(len(self.__record_set), 0, "The log record must not be recorded")

    def test_log_record(self):
        self.__client.post("/__test__/logger/")
        self.assertEquals(len(self.__log_set), 1, "The log set must contain exactly one instance")
        self.assertEquals(len(self.__record_set), len(self.TEST_RECORDS),
                          "The record set must contain exactly four instances")
        log = self.__log_set[0]
        record_index = -1
        for record in self.__record_set:
            desired_info = self.TEST_RECORDS[record_index]
            self.assertEquals(record.level, desired_info['level'], "The log record level must be consistent")
            self.assertEquals(record.message, desired_info['message'], "The log record message must be consistent")
            self.assertEquals(record.log.id, log.id, "All log records must be related to the same record")
            record_index -= 1
