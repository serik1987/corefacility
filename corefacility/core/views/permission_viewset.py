from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.exceptions import NotFound

from core.entity.access_level import AccessLevel, AccessLevelSet
from core.entity.permission import Permission
from core.entity.group import Group, GroupSet
from core.entity.entity_fields.field_managers.permission_manager import PermissionManager
from core.entity.entity_exceptions import EntityNotFoundException
from core.serializers import PermissionSerializer


class PermissionViewSet(GenericViewSet):
    """
    Base viewset for project and application permissions
    """

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
        serializer = PermissionSerializer(permission_list, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs) -> Response:
        """
        Modifies the existent permission

        :param request: request sent by the user
        :param args: request path arguments
        :param kwargs: request path arguments
        :return: response that will be received to the user
        """
        group = self.get_group_or_404(kwargs)
        permission = self.get_permission_or_404(request, group)
        serializer = PermissionSerializer(permission, data=request.data)
        serializer.is_valid(raise_exception=True)
        access_level = self.get_access_level_or_404(serializer.validated_data['access_level_id'])
        self.get_permission_set(request).set(group, access_level)
        return Response({})

    def partial_update(self, request, *args, **kwargs):
        """
        Synonym to the update function
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

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

    def get_permission_or_404(self, request, group: Group) -> Permission:
        """
        Returns a row from the Access Control List corresponding to a given group

        :param request: the request sent by the client
        :param group: a group which permission is interesting
        :return: an instance of core.entity.permission.Permission
        """
        access_level = None
        for current_group, current_access_level in self.iterate_permission_set(request):
            if group.id == current_group.id:
                access_level = current_access_level
                break
        if access_level is None:
            raise NotFound("The method specification is not allowed to set permission for a group which is "
                           "absent in the permission list. Please, use another method.")
        return Permission(group=group, access_level=access_level)

    def get_access_level_or_404(self, level_id) -> AccessLevel:
        if self.access_level_type is None:
            raise NotImplementedError("Please, set the value of access_level_type public property")
        level_set = AccessLevelSet()
        level_set.type = self.access_level_type
        return level_set.get(level_id)

    def iterate_permission_set(self, request: Request):
        """
        Iterates over the permission set

        :param request: the request sent by the client
        :return: generator
        """
        for group, access_level in self.get_permission_set(request):
            if group is not None and group.id != request.project.root_group.id:
                yield group, access_level

    def get_permission_set(self, request: Request) -> PermissionManager:
        """
        Returns set of permissions that has already been saved in the database and exists at the level of
        entities.

        :param request: a request sent by the user
        :return: value of the 'permissions' field for the corresponding entity
        """
        raise NotImplementedError("get_permission_set")
