import logging
from datetime import datetime

from django.test import TestCase
from django.test import client
from django.utils.timezone import make_aware
from parameterized import parameterized

from core.entity.entity_sets.log_set import LogSet


def log_provider():
    return [
        # debug     interface   method      data_index  response_type
        (True,      "api",      "post",     1,          403),
        (False,     "api",      "head",     0,          500),
        (True,      "api",      "post",     0,          200),
        (False,     "api",      "put",      1,          400),
        (True,      "ui",       "get",      0,          400),
        (True,      "api",      "delete",   1,          500),
        (True,      "api",      "put",      0,          403),
        (False,     "api",      "post",     1,          404),
        (False,     "api",      "patch",    1,          200),
        (True,      "api",      "patch",    0,          500),
        (False,     "ui",       "get",      1,          200),
        (True,      "api",      "head",     1,          403),
        (True,      "ui",       "get",      1,          500),
        (True,      "api",      "post",     1,          400),
        (False,     "api",      "delete",   0,          404),
        (True,      "api",      "put",      0,          200),
        (False,     "ui",       "get",      1,          403),
        (True,      "api",      "get",      1,          404),
        (False,     "api",      "patch",    0,          400),
        (False,     "api",      "head",     0,          400),
        (False,     "api",      "patch",    0,          403),
        (False,     "api",      "head",     0,          200),
        (False,     "api",      "delete",   1,          403),
        (False,     "api",      "delete",   1,          200),
        (True,      "api",      "put",      1,          404),
        (True,      "api",      "delete",   1,          400),
        (True,      "api",      "post",     1,          500),
        (True,      "api",      "put",      1,          500),
        (False,     "api",      "head",     0,          404),
        (True,      "api",      "patch",    0,          404),
        (False,     "ui",       "get",      0,          404),

    ]


class TestLogBase(TestCase):
    """
    Provides the base testing facility for the log system.
    """

    REQUEST_PATH = "/__test__/{interface}/{power}/"

    ALL_POWERS = (3, 10)

    ALL_DATA = (
        {"x": 2, "y": 10},
        {"x": 10, "y": 100},
    )

    ALL_EXCEPTIONS = {
        200: None,
        400: "django.core.exceptions.BadRequest",
        403: "django.core.exceptions.PermissionDenied",
        404: "django.http.Http404",
        500: "ValueError",
    }

    __client = None
    __log_set = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.__client = client.Client()

    def setUp(self):
        super().setUp()
        self.__log_set = LogSet()
        logger = logging.getLogger("django.request")
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def tearDown(self):
        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_level)

    @parameterized.expand(log_provider())
    def test_base(self, debug_mode, interface, method, data_index, response_type):
        """
        Provides the base testing features.

        :param debug_mode: Forces certain debug mode (either True or False)
        :param interface: either 'ui' for testing the UI interface or 'api' for testing the API interface
        :param method: the request method
        :param data_index: either 0 or 1 depending on corresponding data
        :param response_type: HTTP response code (200, 400, 403, 404, 500)
        :return:
        """
        with self.settings(DEBUG=debug_mode):
            power = self.ALL_POWERS[data_index]
            request_path = self.REQUEST_PATH.format(interface=interface, power=power)
            request_function = getattr(self.__client, method.lower())
            request_data = self.ALL_DATA[data_index].copy()
            exception = self.ALL_EXCEPTIONS[response_type]
            request_kwargs = {"data": request_data, "secure": False}
            if method.lower() in ["get", "head"] and exception is not None:
                request_kwargs['data']['exception'] = exception
            else:
                if interface == "ui":
                    request_kwargs['content_type'] = client.MULTIPART_CONTENT
                if interface == "api":
                    request_kwargs['content_type'] = "application/json"
                if exception is not None:
                    request_path += "?exception=" + exception
            response = request_function(request_path, **request_kwargs)
            log_number = len(self.__log_set)
            if method.lower() in ["get", "head"] and not debug_mode:
                self.assertEquals(log_number, 0, "All GET request shall not be written when debug mode is off")
            else:
                self.assertEquals(log_number, 1, "This request must be logged")
                log = self.__log_set[0]
                ct = make_aware(datetime.now())
                self.assertLess(log.request_date.get(), ct, "The request date must be less than current date")
                self.assertEquals(log.log_address, request_path.split("?")[0],
                                  "The request path must be stored correctly")
                self.assertEquals(log.request_method.lower(), method.lower(),
                                  "The request method must be stored correctly")
                self.assertEquals(str(log.ip_address), "127.0.0.1",
                                  "The IP address must be 127.0.0.1")
                self.assertEquals(log.response_status, response.status_code,
                                  "The response status must be written correctly")
