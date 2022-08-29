from rest_framework import status
from parameterized import parameterized

from core.entity.log import LogSet
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.log_set_object import LogSetObject
from core.test.entity_set.entity_set_objects.log_record_set_object import LogRecordSetObject

from .base_test_class import BaseTestClass


def log_record_provider():
    """
    Data provider for the only log record test function
    :return: nothing
    """
    return [
        ("basic", 0, "superuser", status.HTTP_200_OK),
        ("light", 0, "superuser", status.HTTP_200_OK),
        ("basic", 1, "superuser", status.HTTP_200_OK),
        ("basic", 2, "superuser", status.HTTP_200_OK),
        ("basic", 3, "superuser", status.HTTP_200_OK),
        ("basic", 4, "superuser", status.HTTP_200_OK),
        ("basic", -1, "superuser", status.HTTP_404_NOT_FOUND),
    ]


class TestLogRecord(BaseTestClass):
    """
    Provides log record testing
    """

    REQUEST_PATH_TEMPLATE = "/api/{version}/logs/{log_id}/records/"

    _user_set_object = None
    _log_set_object = None
    _log_record_set_object = None

    log_id_list = None
    """ List of all log IDs """

    current_log_id = None
    """ Influences on the request_path property """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._log_set_object = LogSetObject(cls._user_set_object.clone())
        cls._log_record_set_object = LogRecordSetObject(cls._log_set_object.clone())
        cls.log_id_list = [log.id for log in cls._log_set_object]

    def setUp(self):
        super().setUp()
        self._container = self._log_record_set_object.clone()

    @parameterized.expand(log_record_provider())
    def test_base_search(self, profile, log_index, token_id, expected_status_code):
        """
        Provides the base search test
        :param profile: 'basic' or 'light' profile
        :param log_index: index of the log in the _log_set_object container
        :param token_id: token ID
        :param expected_status_code: status code that should be
        :return: nothing
        """
        self.current_log_id = self.log_id_list[log_index] if log_index != -1 else max(self.log_id_list) + 1
        if log_index != -1:
            log = LogSet().get(self.current_log_id)
            self.container.filter_by_log(log)
        self._test_search({"profile": profile}, token_id, expected_status_code)

    @property
    def request_path(self):
        return self.REQUEST_PATH_TEMPLATE.format(version=self.API_VERSION, log_id=self.current_log_id)

    def assert_items_equal(self, actual_item, expected_item):
        self.assertEquals(actual_item['id'], expected_item.id, "Unexpected record ID")
        self.assertEquals(str(actual_item['record_time']), str(expected_item.record_time.get()),
                          "Unexpected record time")
        self.assertEquals(actual_item['level'].lower(), expected_item.level.lower(), "Unexpected log record level")
        self.assertEquals(actual_item['message'], expected_item.message, "Unexpected log record message")
