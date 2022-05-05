from rest_framework.permissions import IsAuthenticated


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
