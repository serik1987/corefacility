from datetime import datetime
from django.utils.timezone import make_aware
from ipaddress import ip_address
from parameterized import parameterized

from core.entity.user import User
from core.entity.entity_exceptions import EntityOperationNotPermitted, EntityFieldInvalid
from core.test.data_providers.field_value_providers import string_provider

from .base_test_class import BaseTestClass
from .entity_objects.log_object import LogObject


def request_method_provider():
    return [
        (method, "GET", None, test_number)
        for method in ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH')
        for test_number in (BaseTestClass.TEST_CREATE_AND_LOAD, BaseTestClass.TEST_CHANGE_CREATE_AND_LOAD,
                            BaseTestClass.TEST_CREATE_CHANGE_AND_LOAD)
    ]


def log_string_provider(max_symbols):
    return [args for args in string_provider(0, max_symbols)
            if args[-1] != BaseTestClass.TEST_CREATE_LOAD_AND_CHANGE]


def test_number_provider():
    return [(n,) for n in (
        BaseTestClass.TEST_CREATE_AND_LOAD,
        BaseTestClass.TEST_CHANGE_CREATE_AND_LOAD,
        BaseTestClass.TEST_CREATE_CHANGE_AND_LOAD
    )]


def test_ip_address_provider():
    ip_list_positive = list(map(ip_address,
                           ["127.0.0.1", "255.255.255.255", "0.0.0.0", "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                            "2001:db8:0:0:1::1", "::"]))
    ip_list_positive.append(None)
    test_number_list = [
        BaseTestClass.TEST_CREATE_AND_LOAD,
        BaseTestClass.TEST_CHANGE_CREATE_AND_LOAD,
        BaseTestClass.TEST_CREATE_CHANGE_AND_LOAD
    ]
    sample_ip_address = ip_address("192.168.0.2")
    return [
        (ip_value, sample_ip_address, None, test_number)
        for ip_value in ip_list_positive
        for test_number in test_number_list
    ]


def test_response_status():
    return [(status, 200, None, test_number)
            for status in (100, 599)
            for test_number in (
                BaseTestClass.TEST_CREATE_AND_LOAD,
                BaseTestClass.TEST_CHANGE_CREATE_AND_LOAD,
                BaseTestClass.TEST_CREATE_CHANGE_AND_LOAD
            )]


class TestLog(BaseTestClass):
    """
    Provides test routines for request logs.
    """

    TIMEOUT_MS = 300

    _entity_object_class = LogObject

    def test_object_created_and_deleted(self):
        with self.assertRaises(EntityOperationNotPermitted, msg="Successful log delete"):
            super().test_object_created_and_deleted()

    def test_object_created_changed_and_deleted(self):
        with self.assertRaises(EntityOperationNotPermitted, msg="Successful log delete"):
            super().test_object_created_changed_and_deleted()

    def test_object_created_loaded_and_deleted(self):
        with self.assertRaises(EntityOperationNotPermitted, msg="Successful log delete"):
            super().test_object_created_loaded_and_deleted()

    def test_object_created_loaded_and_changing(self):
        obj = LogObject()
        obj.create_entity()
        obj.reload_entity()
        obj.change_entity_fields()
        with self.assertRaises(EntityOperationNotPermitted, msg="Successful log correction"):
            obj.entity.update()

    def test_request_date_read_only(self):
        self._test_read_only_field("request_date", datetime.now())

    def test_request_date_valid(self):
        obj = LogObject()
        obj.create_entity()
        obj.reload_entity()
        actual_date = obj.entity.request_date.get()
        expected_date = make_aware(datetime.now())
        self.assertLessEqual(actual_date, expected_date, "The log request time is too late")
        delta = expected_date - actual_date
        self.assertLessEqual(delta.total_seconds(), self.TIMEOUT_MS / 1000, "The log request time is too early")

    def test_request_date_transmission(self):
        obj = LogObject()
        expected_date = obj.entity.request_date.get()
        obj.create_entity()
        obj.reload_entity()
        actual_date = obj.entity.request_date.get()
        self.assertEquals(actual_date, expected_date, "The log request date was not correctly retrieved")

    @parameterized.expand(log_string_provider(4096))
    def test_log_address(self, *args):
        self._test_field("log_address", *args)

    @parameterized.expand(request_method_provider())
    def test_request_method(self, *args):
        self._test_field("request_method", *args)

    @parameterized.expand(log_string_provider(4096))
    def test_operation_description(self, *args):
        self._test_field("operation_description", *args)

    @parameterized.expand(log_string_provider(16384))
    def test_request_body(self, *args):
        self._test_field("request_body", *args)

    @parameterized.expand(log_string_provider(16384))
    def test_input_data(self, *args):
        self._test_field("input_data", *args)

    @parameterized.expand(test_number_provider())
    def test_valid_user(self, test_number):
        some_user = User(login="vasily.pupkin")
        some_user.create()
        another_user = User(login="andrey.petrov")
        another_user.create()
        self._test_field("user", some_user, another_user, None, test_number)

    def test_invalid_user(self):
        some_user = User(login="vasily.pupkin")
        obj = LogObject()
        obj.create_entity()
        with self.assertRaises((EntityFieldInvalid, ValueError),
                               msg="Incorrect or inexistent user was successfully assigned"):
            obj.entity.user = some_user
            obj.entity.update()

    @parameterized.expand(test_ip_address_provider())
    def test_ip_address(self, *args):
        self._test_field("ip_address", *args)

    @parameterized.expand(log_string_provider(256))
    def test_geolocation(self, *args):
        self._test_field("geolocation", *args)

    @parameterized.expand(test_response_status())
    def test_response_status(self, *args):
        self._test_field("response_status", *args)

    @parameterized.expand(log_string_provider(16384))
    def test_response_body(self, *args):
        self._test_field("response_body", *args)

    @parameterized.expand(log_string_provider(16384))
    def test_output_data(self, *args):
        self._test_field("output_data", *args)

    def _check_default_fields(self, log):
        self.assertIsNotNone(log.request_date.get(), "The log request date is not defined")
        self.assertEquals(log.log_address, "/path/to/some/resource",
                          "The log address was not retrieved correctly")

    def _check_default_change(self, log):
        self._check_default_fields(log)
        self.assertEquals(log.request_method, "POST", "The request method was not retrieved correctly")
        self.assertEquals(log.operation_description, "Retrieving some resource information",
                          "The operation description was not successfully retrieved")


del BaseTestClass
