from rest_framework.permissions import IsAuthenticated

from .project_related_permission import ProjectRelatedPermission


class AdminOnlyPermission(IsAuthenticated):
    """
    The permission gives all access only to superusers.
    """

    def has_permission(self, request, view):
        """
        Checks whether the user is allowed to perform administrative functions

        :param request: the request
        :param view: the view
        :return: True if the user is allowed, False otherwise
        """
        return bool(super().has_permission(request, view) and request.user.is_superuser)


class NoSupportPermission(IsAuthenticated):
    """
    The permission gives all access to all user except the 'support' user.
    """

    def has_permission(self, request, view):
        """
        Permission check to be done before the immediate request execution.

        :param request: the request
        :param view: the view
        :return: True if the user is allowed, False otherwise
        """
        return bool(super().has_permission(request, view) and not request.user.is_support)


class GroupPermission(IsAuthenticated):
    """
    Defines all available permissions for the user group
    """

    SAFE_METHODS = ["GET", "HEAD", "OPTIONS"]

    def has_object_permission(self, request, view, group):
        return request.method in self.SAFE_METHODS or group.governor.id == request.user.id or request.user.is_superuser


class ProjectPermission(IsAuthenticated):
    """
    Defines individual permissions for project CRUD operations as well as project avatar update.
    """

    SAFE_METHODS = ["GET", "HEAD", "OPTIONS"]

    def has_object_permission(self, request, view, project):
        """
        Defines whether the client has an access to a particular project

        :param request: the HTTP request sent by a particular client
        :param view: an instance of the ProjectViewSet
        :param project: a particular project which permissions shall be calculated
        :return: True if the particular project operation is allowed, False if the operation is prohibited
        """
        return request.method in self.SAFE_METHODS or \
            request.user.is_superuser or \
            project.is_user_governor


class ProjectSettingsPermission(ProjectRelatedPermission):
    """
    Defines individual permissions
    """

    def has_project_permission(self, request, view, project, access_level, is_user_superuser):
        """
        Checks whether the user can deal with a certain particular project

        :param request: a currently processing request
        :param view: an API view responsible for processing the request
        :param project: a project the user is trying to work on
        :param access_level: a project access level calculated for a particular user
        :param is_user_superuser: True if the user has superuser rights for the project, False otherwise
        :return: True if the access shall be granted. False if the access shall be denied.
        """
        return is_user_superuser
