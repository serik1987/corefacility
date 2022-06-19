import urllib.parse

from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from core.generic_views import SetCookieMixin
from core.permissions import AdminOnlyPermission
from core.entity.entry_points.synchronizations import SynchronizationsEntryPoint


class SynchronizationView(SetCookieMixin, APIView):
    """
    Synchronizes all user accounts with an external source
    """

    permission_classes = [AdminOnlyPermission]

    def post(self, request: Request, *args, **kwargs):
        synchronization_options = request.data
        output = SynchronizationsEntryPoint.synchronize(request.user, **synchronization_options)
        return Response(output)
