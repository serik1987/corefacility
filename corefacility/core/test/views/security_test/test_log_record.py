from rest_framework import status
from parameterized import parameterized

from core.entity.log_record import LogRecord, LogRecordSet
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.log_set_object import LogSetObject
from core.test.entity_set.entity_set_objects.log_record_set_object import LogRecordSetObject

from .base_log_test import BaseLogTest


def log_retrieve_provider():
    """
    Provides the data for the log retrieve test
    :return: list of arguments to the test_log_retrieved function
    """
    return [
        ((0, 0), "superuser", status.HTTP_200_OK),
        ((0, 1), "superuser", status.HTTP_200_OK),
        ((0, 2), "superuser", status.HTTP_404_NOT_FOUND),
        ((1, 1), "superuser", status.HTTP_404_NOT_FOUND),
        ((1, 2), "superuser", status.HTTP_200_OK),
        ((1, 3), "superuser", status.HTTP_200_OK),
        ((1, 4), "superuser", status.HTTP_404_NOT_FOUND),
        ((2, 4), "superuser", status.HTTP_200_OK),
        ((3, 5), "superuser", status.HTTP_200_OK),
        ((-1, 5), "superuser", status.HTTP_404_NOT_FOUND),
        ((0, -1), "superuser", status.HTTP_404_NOT_FOUND),
        ((0, 0), "ordinary_user", status.HTTP_403_FORBIDDEN),
        ((0, 2), "ordinary_user", status.HTTP_403_FORBIDDEN),
        ((0, 0), None, status.HTTP_401_UNAUTHORIZED),
        ((0, 2), None, status.HTTP_401_UNAUTHORIZED),
    ]


def log_modify_provider():
    """
    Provides the data for log modification test
    :return: list of arguments for the log_record_create, log_record_update and log_record_destroy functions
    """
    return [
        ((0, 0), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((0, 1), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((0, 2), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((1, 1), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((1, 2), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((1, 3), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((1, 4), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((2, 4), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((3, 5), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((-1, 5), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((0, -1), "superuser", status.HTTP_405_METHOD_NOT_ALLOWED),
        ((0, 0), "ordinary_user", status.HTTP_403_FORBIDDEN),
        ((0, 2), "ordinary_user", status.HTTP_403_FORBIDDEN),
        ((0, 0), None, status.HTTP_401_UNAUTHORIZED),
        ((0, 2), None, status.HTTP_401_UNAUTHORIZED),
    ]


class TestLogRecord(BaseLogTest):
    """
    Contains test cases for the /api/v1/logs/<log_id>/records/<record_id>/ feature
    """

    LOG_RECORD_SET_PATH = "/api/{version}/logs/%d/records/".format(version=BaseLogTest.API_VERSION)

    LOG_RECORD_PATH = "/api/{version}/logs/%d/records/%d/".format(version=BaseLogTest.API_VERSION)

    _tested_entity = LogRecord
    """ Entity to test """

    _entity_set = LogRecordSet()
    """ The entity set object to be used for checking the response results. The object must be initialized. """

    _user_set_object = None
    """ Provides list of sample users """

    _log_set_object = None
    """ Provides list of sample logs """

    _log_id_list = None
    """ List of log IDs """

    _log_record_set_object = None
    """ Provides list of sample log records """

    _log_record_id_list = None
    """ List of log record IDs """

    NEW_RECORD_DATA = {
        "level": "DEB",
        "message": "Nothing important"
    }

    @classmethod
    def get_log_and_record_id(cls, log_and_record_index):
        """
        Transforms the log and record index to the log and record ID
        :param log_and_record_index: a tuple of (log_index, record_index) where log_index is a log_index within the
            log entity set and record_index is the record index within the record entity set. Use -1 to generate
            some non-existent ID (negative test)
        :return: a tuple where the first element is log ID and the second one is record ID
        """
        log_index, record_index = log_and_record_index
        log_id = cls._log_id_list[log_index] if log_index != -1 else max(cls._log_id_list) + 1
        log_record_id = cls._log_record_id_list[record_index] \
            if record_index != -1 else max(cls._log_record_id_list) + 1
        return log_id, log_record_id

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._log_set_object = LogSetObject(cls._user_set_object.clone())
        cls._log_id_list = [log.id for log in cls._log_set_object]
        cls._log_record_set_object = LogRecordSetObject(cls._log_set_object.clone())
        cls._log_record_id_list = [log_record.id for log_record in cls._log_record_set_object]

    @parameterized.expand(log_modify_provider())
    def test_log_create(self, log_and_record_index, token_id, expected_status_code):
        """
        Tests whether new record can be created
        :param log_and_record_index: a tuple of (log_index, record_index) where log_index is a log_index within the
            log entity set and record_index is the record index within the record entity set. Use -1 to generate
            some non-existent ID (negative test)
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses
        :param expected_status_code: status code to be expected
        """
        log_id, _ = self.get_log_and_record_id(log_and_record_index)
        auth_headers = self.get_authorization_headers(token_id)
        response = self.client.post(self.LOG_RECORD_SET_PATH % log_id, self.NEW_RECORD_DATA, format="json",
                                    **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")

    @parameterized.expand(log_retrieve_provider())
    def test_log_retrieved(self, log_and_record_index, token_id, expected_status_code):
        """
        Tests whether single log record can be successfully downloaded
        :param log_and_record_index: a tuple of (log_index, record_index) where log_index is a log_index within the
            log entity set and record_index is the record index within the record entity set. Use -1 to generate
            some non-existent ID (negative test)
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses
        :param expected_status_code: status code to be expected
        """
        log_id, record_id = self.get_log_and_record_id(log_and_record_index)
        log_and_record_path = self.LOG_RECORD_PATH % (log_id, record_id)
        auth_headers = self.get_authorization_headers(token_id)
        response = self.client.get(log_and_record_path, **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status code")
        if response.status_code == status.HTTP_200_OK:
            actual_record = response.data
            expected_record = LogRecordSet().get(record_id)
            self.assertEquals(str(actual_record['record_time']), str(expected_record.record_time.get()),
                              "Unexpected record time")
            self.assertEquals(actual_record['level'].lower(), expected_record.level.lower(),
                              "Unexpected record level")
            self.assertEquals(actual_record['message'], expected_record.message, "Unexpected record message")

    @parameterized.expand(log_modify_provider())
    def test_log_update(self, log_and_record_index, token_id, expected_status_code):
        """
        Tests whether single log can be modified
        :param log_and_record_index: a tuple of (log_index, record_index) where log_index is a log_index within the
            log entity set and record_index is the record index within the record entity set. Use -1 to generate
            some non-existent ID (negative test)
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses
        :param expected_status_code: status code to be expected
        """
        log_and_record_id = self.get_log_and_record_id(log_and_record_index)
        log_and_record_path = self.LOG_RECORD_PATH % log_and_record_id
        auth_headers = self.get_authorization_headers(token_id)
        response = self.client.patch(log_and_record_path, self.NEW_RECORD_DATA, format="json", **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")

    @parameterized.expand(log_modify_provider())
    def test_log_destroy(self, log_and_record_index, token_id, expected_status_code):
        """
        Tests whether single log can be destroyed
        :param log_and_record_index: a tuple of (log_index, record_index) where log_index is a log_index within the
            log entity set and record_index is the record index within the record entity set. Use -1 to generate
            some non-existent ID (negative test)
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses
        :param expected_status_code: status code to be expected
        """
        log_and_record_id = self.get_log_and_record_id(log_and_record_index)
        log_and_record_path = self.LOG_RECORD_PATH % log_and_record_id
        auth_headers = self.get_authorization_headers(token_id)
        response = self.client.delete(log_and_record_path, **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")


del BaseLogTest
