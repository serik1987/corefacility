from django.utils.module_loading import import_string
from django.core.exceptions import BadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def test_ui(request, n):
    """
    The test UI request handler

    :param request: the request to be processed
    :param n: Some request path parameter
    :return: The HTTP response
    """
    if "exception" in request.GET.keys():
        exception_string = request.GET["exception"]
        try:
            exception = import_string(exception_string)
        except ImportError:
            exception = BadRequest
        raise exception()
    data = request.GET.copy()
    data.update(request.POST)
    try:
        x = int(data['x'])
        n = int(n)
        y = str(x**n)
    except ValueError:
        y = -1
    context = {"y": y, "data": data}
    return render(request, "core/tests/test_ui.html", context)
