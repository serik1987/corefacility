from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from ..generic_views import EntityViewSet
from ..entity.group import GroupSet
from ..entity.user import UserSet
from ..entity.entity_exceptions import EntityOperationNotPermitted
from ..serializers import GroupSerializer, UserListSerializer
from ..permissions import GroupPermission


class GroupViewSet(EntityViewSet):
    """
    Deals with list of groups.
    """

    list_filters = {
        "name": EntityViewSet.standard_filter_function("q", str),
    }

    entity_set_class = GroupSet
    list_serializer_class = GroupSerializer
    detail_serializer_class = GroupSerializer
    permission_classes = [GroupPermission]

    @action(methods=["GET"], detail=True, url_path="users", url_name="users")
    def get_user_list(self, request, *args, **kwargs):
        """
        Retrieves list of all group members

        :param request: information about the request processed
        :param args: additional arguments extracted from the request path
        :param kwargs: additional keyword arguments extracted from the request path
        :return:
        """
        group = self.get_object()
        page = self.paginate_queryset(group.users)
        serializer = UserListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=["DELETE"], detail=True, url_path=r'users/(?P<user_lookup>\w+)', url_name="user-delete")
    def delete_user(self, request, *args, **kwargs):
        group = self.get_object()
        user = self.get_entity_or_404(UserSet(), kwargs['user_lookup'])
        try:
            group.users.remove(user)
        except EntityOperationNotPermitted:
            raise PermissionDenied()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def filter_queryset(self, queryset):
        """
        Provides additional queryset filtration according to security considerations.

        :param queryset: the initial queryset
        :return: the filtered queryset
        """
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if not user.is_superuser:
            queryset.user = user
        return queryset
