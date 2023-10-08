from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound

from ..pagination import CorePagination
from ru.ihna.kozhukhov.core_application.generic_views import EntityViewSet
from ru.ihna.kozhukhov.core_application.entity.group import GroupSet
from ru.ihna.kozhukhov.core_application.entity.entity_sets.user_set import UserSet
from ..exceptions.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException
from ru.ihna.kozhukhov.core_application.serializers import GroupSerializer, UserListSerializer
from ru.ihna.kozhukhov.core_application.permissions import GroupPermission


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

    def destroy(self, request, *args, **kwargs):
        """
        Destroys the object

        :param request: the HTTP request received from the client
        :param args: request path arguments
        :param kwargs: request path keyword arguments
        :return: nothing
        """
        group = self.get_object()
        if "force" in request.query_params:
            group.force_delete()
        else:
            group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        try:
            user_lookup = int(kwargs['user_lookup'])
        except ValueError:
            user_lookup = kwargs['user_lookup']
        user = self.get_entity_or_404(UserSet(), user_lookup)
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
        group_set = GroupSet()
        if not request.user.is_superuser and "all" not in request.query_params:
            group_set.user = request.user
        try:
            group = group_set.get(int(kwargs['lookup']))
        except EntityNotFoundException:
            raise NotFound()
        self.check_object_permissions(request, group)
        group_users = {user.id for user in group.users}
        user_set = UserSet()
        user_set.is_support = False
        if 'q' in request.query_params:
            user_set.name = request.query_params['q']
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
        if "mustbegovernor" in self.request.query_params:
            queryset.governor = self.request.user
        return queryset
