from rest_framework.permissions import IsAuthenticated

from core.entity.project import ProjectSet
from core.generic_views.entity_view_mixin import EntityViewMixin


class ProjectRelatedPermission(IsAuthenticated):
    """
    All permission required for project working. Such permissions will be granted when:

    a. The project ID or alias is presented in the request path and its template has a 'project_lookup' name
        (otherwise, error 500 will be returned)
    b. The user is authorized (otherwise, error 401 will be returned
    c. One of the following conditions are satisfied (either error 404 or error 403 will be returned):
        - the user is superuser;
        - the user belongs to the project's root group;
        - the user belongs to a group for which the access level was set to a value higher than 'no_access'
    d. Additional conditions added to the subclasses were hold.
    """

    access_level = None
    is_user_governor = None

    def has_permission(self, request, view):
        """
        Checks whether the user is permitted to execute such a request

        :param request: the request a user is trying to execute
        :param view: the view corresponding to the request
        :return: True if the access shall be granted, False if the access shall be denied
        """
        if not super().has_permission(request, view):
            return False
        lookup = view.kwargs['project_lookup']
        try:
            lookup = int(lookup)
        except ValueError:
            pass
        project_set = ProjectSet()
        if not request.user.is_superuser:
            project_set.user = request.user
        request.project = EntityViewMixin.get_entity_or_404(project_set, lookup)
        if request.user.is_superuser:
            request.project_access_level = "full"
            request.is_project_superuser = True
        else:
            request.project_access_level = request.project.user_access_level
            request.is_project_superuser = request.project.is_user_governor
        return self.has_project_permission(request, view, request.project, request.project_access_level,
                                           request.is_project_superuser)

    def has_project_permission(self, request, view, project, access_level, is_project_superuser):
        """
        Checks whether the user can deal with a certain particular project

        :param request: a currently processing request
        :param view: an API view responsible for processing the request
        :param project: a project the user is trying to work on
        :param access_level: a project access level calculated for a particular user
        :param is_project_superuser: True given that at least one of the following conditions are True:
            - the user is project governor;
            - the user is governor of the group which project permissions are set to 'full'
        :return: True if the access shall be granted. False if the access shall be denied.
        """
        return True
