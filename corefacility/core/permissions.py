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
