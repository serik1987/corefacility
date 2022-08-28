import platform
from datetime import timedelta

from django.utils.timezone import make_naive
from rest_framework import status
from parameterized import parameterized

from core.entity.log import LogSet
from core.test.entity_set.entity_set_objects.log_set_object import LogSetObject
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject

from .base_test_class import BaseTestClass


def base_search_provider():
    """
    Provides the data for the test_base_search test function
    :return: list of test_base_search function arguments
    """
    return [
        ("basic", "superuser", status.HTTP_200_OK),
        ("light", "superuser", status.HTTP_200_OK),
        ("basic", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("basic", None, status.HTTP_401_UNAUTHORIZED),
    ]


def date_filter_provider():
    """
    Provides the data for the date_from and date_to filters
    :return: list of test_date_from_filter and test_date_to_filter arguments
    """
    return [
        (20, "aware"),
        (30, "aware"),
        (10, "naive"),
        (30, "naive"),
        (10, "aware"),
    ]


def ip_address_provider():
    """
    Provides the data for the test_ip_address_filter
    :return: list of test_ip_address_filter function arguments
    """
    return [
        ("127.0.0.1", status.HTTP_200_OK),
        ("2001:db8:0:0:1::1", status.HTTP_200_OK),
        ("::1", status.HTTP_200_OK),
        ("8.8.8.8", status.HTTP_200_OK),
        ("DZFSHGDFG", status.HTTP_400_BAD_REQUEST),
        ("", status.HTTP_200_OK)
    ]


def user_filter_provider():
    """
    Provides the data for the test_user_filter test
    :return:  list of test_user_filter function arguments
    """
    return [
        (0, status.HTTP_200_OK),
        (1, status.HTTP_200_OK),
        (2, status.HTTP_200_OK),
        (3, status.HTTP_200_OK),
        (4, status.HTTP_200_OK),
        (-1, status.HTTP_400_BAD_REQUEST),
    ]


class TestLog(BaseTestClass):
    """
    Provides the testing features for the log lists
    """

    _request_path = "/api/{version}/logs/".format(version=BaseTestClass.API_VERSION)

    superuser_required = True
    ordinary_user_required = True

    user_set_object = None
    log_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user_set_object = UserSetObject()
        cls.log_set_object = LogSetObject(cls.user_set_object.clone())

    def setUp(self):
        super().setUp()
        self._container = self.log_set_object.clone()
        self._container.sort()

    @parameterized.expand(base_search_provider())
    def test_basic_search(self, profile, token_id, expected_status_code):
        """
        Provides the basic search test
        :param profile: 'basic' or 'light' profile. Both of them influence on number of logs per page
        :param token_id: token ID
        :param expected_status_code: expected status code
        """
        self._test_search({"profile": "basic"}, token_id, expected_status_code)

    @parameterized.expand(date_filter_provider())
    def test_date_from_filter(self, cnt, tz_type):
        """
        Tests the 'date_from' filter
        :param cnt: number of logs that shall be found after application of the date_from filter
        :param tz_type: 'aware' to send the 'date_from' filter together with timezone info, 'naive' if you don't
            want to do it
        """
        if platform.system().lower() == "windows":
            self.skipTest("The test was not designed under WINDOWS platform")
        log_set = LogSet()
        log_date = log_set[cnt].request_date.get() - timedelta(milliseconds=1)
        self.container.filter_by_request_date_from(log_date)
        if tz_type == "naive":
            log_date = make_naive(log_date)
        self._test_search({"profile": "basic", "from": str(log_date)}, "superuser", status.HTTP_200_OK)

    @parameterized.expand(date_filter_provider())
    def test_date_to_filter(self, cnt, tz_type):
        """
        Tests the 'date_to' filter
        :param cnt: number of logs that shall be omitted during the application of this filter
        :param tz_type: "naive" to use naive datetime in the requests, "aware" to use aware format
        """
        if platform.system().lower() == "windows":
            self.skipTest("The test is not suitable under this platform")
        log_set = LogSet()
        log_date = log_set[cnt].request_date.get() + timedelta(milliseconds=1)
        self.container.filter_by_request_date_to(log_date)
        if tz_type == "naive":
            log_date = make_naive(log_date)
        self._test_search({"profile": "basic", "to": str(log_date)}, "superuser", status.HTTP_200_OK)

    @parameterized.expand([("from",), ("to",)])
    def test_date_request_bad_value(self, query_param):
        """
        Provides negative tests for the 'from' and 'to' fields
        :param query_param: query param to test
        """
        self._test_search({query_param: "sjhjkfh"}, "superuser", status.HTTP_400_BAD_REQUEST)

    @parameterized.expand(ip_address_provider())
    def test_ip_address_filter(self, ip_address, response_code):
        """
        Provides tests for the ip_address field
        :param ip_address: IP address to substitute
        :param response_code: expected response code
        """
        if response_code == status.HTTP_200_OK and ip_address != "":
            self.container.filter_by_ip_address(ip_address)
        self._test_search({"profile": "basic", "ip_address": ip_address}, "superuser", response_code)

    @parameterized.expand(user_filter_provider())
    def test_user_filter(self, user_index, response_code):
        """
        Tests the user filter
        :param user_index: index of the user within the user_set_object container or -1 to us
        :param response_code: expected response code
        """
        user_id_list = [user.id for user in self.user_set_object]
        user_id = user_id_list[user_index] if user_index != -1 else max(user_id_list) + 1
        if response_code == status.HTTP_200_OK:
            self.container.filter_by_user(self.user_set_object[user_index])
        self._test_search({"profile": "basic", "user": user_id}, "superuser", response_code)

    def assert_items_equal(self, actual_item, desired_item):
        """
        Compares two list item
        :param actual_item: the item received within the response
        :param desired_item: the item taken from the container
        :return: nothing
        """
        self.assertEquals(actual_item['id'], desired_item.id, "Item IDs are not the same")
        self.assertEquals(str(actual_item['request_date'],), str(desired_item.request_date),
                          "Item request dates are not equal")
        if desired_item.log_address is not None:
            self.assertEquals(actual_item['log_address'], desired_item.log_address, "Unexpected log address")
        if desired_item.request_method is not None:
            self.assertEquals(actual_item['request_method'], desired_item.request_method, "Unexpected request method")
        self.assertEquals(actual_item['operation_description'], desired_item.operation_description,
                          "Unexpected operation description")
        if actual_item['user'] is None:
            self.assertIsNone(desired_item.user, "Unexpected user in the log output")
        else:
            self.assertEquals(actual_item['user']['id'], desired_item.user.id, "Unexpected user ID")
            self.assertEquals(actual_item['user']['login'], desired_item.user.login, "Unexpected user login")
            self.assertEquals(actual_item['user']['name'], desired_item.user.name, "Unexpected user name")
            self.assertEquals(actual_item['user']['surname'], desired_item.user.surname, "Unexpected user surname")
        self.assertEquals(str(actual_item['ip_address']), str(desired_item.ip_address), "Unexpected IP address")
        self.assertEquals(actual_item['geolocation'], desired_item.geolocation, "Unexpected geolocation")
        self.assertEquals(actual_item['response_status'], desired_item.response_status,
                          "The log in the response body doesn't match to the expected one: unexpected response status")


del BaseTestClass
