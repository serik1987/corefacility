import logging

from django.views.generic.base import View
from django.utils.module_loading import import_string
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response

request_logger = logging.getLogger("django.corefacility.test")


@api_view(View.http_method_names)
@permission_classes([])
@throttle_classes([])
def test_api(request, n):
    """
    The API test request handler

    :param request: the request itself
    :param n: request path parameter
    :return: the HTTP response
    """
    if "exception" in request.GET.keys():
        try:
            exception = import_string(request.GET['exception'])
            raise exception()
        except ImportError:
            pass
    data = request.GET.copy()
    data.update(request.data)
    try:
        x = int(data['x'])
        n = int(n)
        y = x**n
    except Exception:
        y = -1
    return Response({
        "y": y,
        "data": data
    })


@api_view(['get', 'post'])
@permission_classes([])
@throttle_classes([])
def test_logger(request):
    """
    The logger testing system

    :param request: the request itself
    :return: nothing
    """
    request_logger.debug("This is the debugging test message", extra={"request": request})
    request_logger.info("This is an info test message", extra={"request": request})
    request_logger.warning("This is a warning test message", extra={"request": request})
    request_logger.error("This is an error test message", extra={"request": request})
    request_logger.critical("This is a critical test message", extra={"request": request})
    return Response({})
