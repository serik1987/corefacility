from django.views.generic.base import View
from django.utils.module_loading import import_string
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(View.http_method_names)
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
