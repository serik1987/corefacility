from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet


class PermissionViewSet(GenericViewSet):
    """
    Base viewset for project and application permissions
    """

    def list(self, request, *args, **kwargs):
        print(request, repr(request.user))
        return Response({})
