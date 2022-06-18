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

    def get(self, request: Request, *args, **kwargs):
        synchronization_options = {name: value for name, value in request.query_params.items()}
        output = SynchronizationsEntryPoint.synchronize(**synchronization_options)
        if output['next_options'] is not None:
            next_url = reverse("core:account-synchronization", args=args, kwargs=kwargs) + "?" + \
                       urllib.parse.urlencode(output['next_options'])
        else:
            next_url = None
        return Response({
            "next_url": next_url,
            "details": output['details']
        })

    def do_something(self, *args, **kwargs):
        print(args)
        print(kwargs)
