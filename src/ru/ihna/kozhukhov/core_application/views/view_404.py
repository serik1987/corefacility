from rest_framework.views import APIView
from rest_framework.exceptions import NotFound


class View404(APIView):
    """
    The API request to non-existent resource
    """

    permission_classes = []

    def __getattr__(self, name):
        if name in self.http_method_names:
            def func(request, *args, **kwargs):
                raise NotFound()
            return func
        else:
            raise AttributeError("Not a valid HTTP method")
