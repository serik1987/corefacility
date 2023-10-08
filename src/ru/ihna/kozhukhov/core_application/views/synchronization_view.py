from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from ..generic_views import SetCookieMixin
from ..permissions import AdminOnlyPermission
from ..entry_points.synchronizations import SynchronizationsEntryPoint


class SynchronizationView(SetCookieMixin, APIView):
    """
    Synchronizes all user accounts with an external source
    """

    permission_classes = [AdminOnlyPermission]

    def post(self, request: Request, *args, **kwargs):
        synchronization_options = request.data
        output = SynchronizationsEntryPoint.synchronize(request.user, **synchronization_options)
        return Response(output)
