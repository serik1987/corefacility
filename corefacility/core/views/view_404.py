from rest_framework.views import APIView
from rest_framework.exceptions import NotFound


class View404(APIView):
    """
    The API request to non-existent resource.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.
        """
        raise NotFound()
