from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..pagination import CorePagination
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

    @action(methods=["GET", "POST"], detail=True, url_path="users", url_name="users")
    def users(self, request, *args, **kwargs):
        """
        Working with user list
        """
        if request.method == "GET":
            return self.get_user_list(request, *args, **kwargs)
        elif request.method == "POST":
            return self.set_user_list(request, *args, **kwargs)

    def get_user_list(self, request, *args, **kwargs):
        """
        Retrieves list of all group members
        """
        group = self.get_object()
        page = self.paginate_queryset(group.users)
        serializer = UserListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def set_user_list(self, request, *args, **kwargs):
        """
        Adds user to the group users.
        """
        group = self.get_object()
        try:
            user_id = int(request.data['user_id'])
        except (KeyError, ValueError):
            raise ValidationError(detail="The request body must contain the only field: 'user_id'. "
                                         "The value of this field must be integer")
        user = self.get_entity_or_404(UserSet(), user_id)
        try:
            group.users.add(user)
        except EntityOperationNotPermitted:
            raise PermissionDenied()
        serializer = UserListSerializer(user, many=False)
        return Response(serializer.data)

    @action(methods=["DELETE"], detail=True, url_path=r'users/(?P<user_lookup>\w+)', url_name="user-delete")
    def delete_user(self, request, *args, **kwargs):
        """
        Removes user from the group users

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        group = self.get_object()
        user = self.get_entity_or_404(UserSet(), kwargs['user_lookup'])
        try:
            group.users.remove(user)
        except EntityOperationNotPermitted:
            raise PermissionDenied()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=True, url_path=r'user-suggest', url_name="user-suggest")
    def suggest_user(self, request, *args, **kwargs):
        """
        Suggests the user for adding

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        group = self.get_object()
        group_users = {user.id for user in group.users}
        user_set = UserSet()
        user_set.is_support = False
        index = 0
        user_list = []
        for user in user_set:
            if user.id not in group_users:
                serializer = UserListSerializer(user, many=False)
                user_list.append(serializer.data)
                index += 1
            if index >= CorePagination.PAGE_SIZES['light']:
                break
        return Response(user_list)

    def filter_queryset(self, queryset):
        """
        Provides additional queryset filtration according to security considerations.

        :param queryset: the initial queryset
        :return: the filtered queryset
        """
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if not user.is_superuser and "all" not in self.request.query_params:
            queryset.user = user
        return queryset
