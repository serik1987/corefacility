from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from core.entity.permission import Permission
from core.entity.entity_fields.field_managers.permission_manager import PermissionManager
from core.serializers import PermissionSerializer


class PermissionViewSet(GenericViewSet):
    """
    Base viewset for project and application permissions
    """

    def list(self, request, *args, **kwargs):
        permission_list = []
        for group, access_level in self.get_permission_set(request):
            if group is not None and group.id != request.project.root_group.id:
                permission = Permission(group=group, access_level=access_level)
                permission_list.append(permission)
        serializer = PermissionSerializer(permission_list, many=True)
        return Response(serializer.data)

    def get_permission_set(self, request: Request) -> PermissionManager:
        """
        Returns set of permissions that has already been saved in the database and exists at the level of
        entities.

        :param request: a request sent by the user
        :return: value of the 'permissions' field for the corresponding entity
        """
        raise NotImplementedError("get_permission_set")
