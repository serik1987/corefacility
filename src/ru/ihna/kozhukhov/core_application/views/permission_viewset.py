from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import NotFound, PermissionDenied

from ..entity.permission import Permission
from ..entity.group import Group, GroupSet
from ..exceptions.entity_exceptions import EntityNotFoundException, EntityOperationNotPermitted
from ..serializers import PermissionOutputSerializer, PermissionInputSerializer
from ..generic_views import SetCookieMixin
from ..permissions import ProjectSettingsPermission


class PermissionViewSet(SetCookieMixin, GenericViewSet):
    """
    Base viewset for project and application permissions
    """

    permission_classes = [ProjectSettingsPermission]

    lookup_url_kwarg = "pk"

    access_level_type = None
    """ Defines a certain access level type """

    def list(self, request, *args, **kwargs) -> Response:
        """
        List of all permissions

        :param request: request sent by the client
        :param args: request path arguments
        :param kwargs: request path arguments
        :return: response that will be received to the client
        """
        permission_list = []
        for group, access_level in self.iterate_permission_set(request):
            permission = Permission(group=group, access_level=access_level)
            permission_list.append(permission)
        serializer = PermissionOutputSerializer(permission_list, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Adds new rule to the Access Control List or modifies an existent one

        :param request: the HTTP request sent by the client application
        :param args: request arguments
        :param kwargs: request keyword arguments
        :return: the HTTP response that will be sent to the client application
        """
        input_serializer = PermissionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        input_serializer.save()
        try:
            permission = input_serializer.instance
            request.project.permissions.set(permission.group, permission.access_level)
        except EntityOperationNotPermitted:
            raise PermissionDenied(detail="Entity-level restrictions applied.")
        output_serializer = PermissionOutputSerializer(permission, many=False)
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Destroys existent permission from the permission set

        :param request: the HTTP request sent by the client application
        :param args: request path arguments
        :param kwargs: request path keyword arguments
        :return: the HTTP response that will be sent to the client application
        """
        group = self.get_group_or_404(kwargs)
        if group.id == request.project.root_group.id:
            raise PermissionDenied(detail="Removing the root group is denied.")
        group_deleted = False
        for current_group, _ in self.iterate_permission_set(request):
            if current_group.id == group.id:
                request.project.permissions.delete(group)
                group_deleted = True
        code = status.HTTP_204_NO_CONTENT if group_deleted else status.HTTP_404_NOT_FOUND
        return Response(status=code)

    def get_group_or_404(self, kwargs) -> Group:
        """
        Returns a group which ID is located in the group path.
        If this is impossible to find such a group, raises exception 404.

        :param kwargs: results of the path resolve
        :return: an instance of core.entity.group.Group
        """
        try:
            group_id = int(kwargs[self.lookup_url_kwarg])
        except ValueError:
            raise NotFound("No valid group ID has been provided")
        try:
            group = GroupSet().get(group_id)
        except EntityNotFoundException:
            raise NotFound("The user group with a given ID was not found")
        return group

    def iterate_permission_set(self, request: Request):
        """
        Iterates over the permission set

        :param request: the request sent by the client
        :return: generator
        """
        for group, access_level in request.project.permissions:
            if group is not None and group.id != request.project.root_group.id:
                yield group, access_level
