from django.test import client as client_module


def log_provider():
    """
    Provides sample data for the 'make_test_request' function based on pairwise test method technique
    :return: list of tuples with the following data
        - debug mode (True, False)
        - interface ("api", "ui")
        - method ("get", "head", "post", ...)
        - data_index number of data in the ALL_POWERS and ALL_DATA tuples
        - response type (200, 403, 404, 500)
    """
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


class SampleLogMixin:
    """
    This is a helper class that helps to create sample logs
    """

    REQUEST_PATH = "/__test__/{interface}/{power}/"
    """ The request path for the sample log request """

    ALL_POWERS = (3, 10)

    ALL_EXCEPTIONS = {
        200: None,
        400: "django.core.exceptions.BadRequest",
        403: "django.core.exceptions.PermissionDenied",
        404: "django.http.Http404",
        500: "django.core.exceptions.ObjectDoesNotExist",
    }

    ALL_DATA = (
        {"x": 2, "y": 10},
        {"x": 10, "y": 100},
    )

    @classmethod
    def fill_sample_logs(cls):
        """
        Fills the log list by sending some sample requests
        :return: nothing
        """
        client = client_module.Client(raise_request_exception=False)
        for debug_mode, interface, method, data_index, response_type in log_provider():
            cls.make_test_request(client, interface, method, data_index, response_type)

    @classmethod
    def make_test_request(cls, client, interface, method, data_index, response_type):
        """
        Executes the testing request
        :param client: the HTTP client that shall be used for making such test request
        :param interface: either 'ui' for testing the UI interface or 'api' for testing the API interface
        :param method: the request method
        :param data_index: either 0 or 1 depending on corresponding data
        :param response_type: HTTP response code (200, 400, 403, 404, 500)
        :return: the HTTP response
        """
        power = cls.ALL_POWERS[data_index]
        request_path = cls.REQUEST_PATH.format(interface=interface, power=power)
        request_function = getattr(client, method.lower())
        request_data = cls.ALL_DATA[data_index].copy()
        exception = cls.ALL_EXCEPTIONS[response_type]
        request_kwargs = {"data": request_data, "secure": False}
        if method.lower() in ["get", "head"] and exception is not None:
            request_kwargs['data']['exception'] = exception
        else:
            if interface == "ui":
                request_kwargs['content_type'] = client_module.MULTIPART_CONTENT
            if interface == "api":
                request_kwargs['content_type'] = "application/json"
            if exception is not None:
                request_path += "?exception=" + exception
        response = request_function(request_path, **request_kwargs)
        return response
