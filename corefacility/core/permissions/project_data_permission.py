from core.entity.project import Project

from .project_related_permission import ProjectRelatedPermission


class ProjectDataPermission(ProjectRelatedPermission):
    """
    These permissions are used for working with common data operations.

    The permissions are method-based. This means that:
    - any user with 'full' or 'data_full' privileges can complete GET, HEAD, OPTIONS, POST, PUT, PATCH and DELETE
        requests
    - any user with 'data_add' priviledges can complete any request from that list except DELETE
    - any user with 'data_process' priviledges can complete GET, HEAD and OPTIONS request. Also, he can complete
        POST, PUT and PATCH requests if the view has been marked its data gathering way as 'upload'
    - any user with 'data_view' priviledges can complete GET, HEAD and OPTIONS requests
    - any other user can't execute any kind of request
    """

    method_access_table = {
        "uploading": {
            "data_add": {'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'},
            "data_process": {'GET', 'HEAD', 'OPTIONS'},
            "data_view": {'GET', 'HEAD', 'OPTIONS'},
        },
        "processing": {
            "data_add": {'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'},
            "data_process": {'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH'},
            "data_view": {'GET', 'HEAD', 'OPTIONS'},
        }
    }

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
        access_level = Project.get_proper_access_level(access_level)
        if not hasattr(view, "data_gathering_way"):
            raise NotImplementedError("SECURITY ALERT: to use the view you are trying to use please define the "
                                      "way of data gathering: set public variable data_gathering_way='uploading' if "
                                      "your view uploads the data from the client or data_gathering_way='processing' "
                                      "if your view processes existing data on the server")
        if access_level == "full" or access_level == "data_full":
            return True
        return request.method.upper() in self.method_access_table[view.data_gathering_way][access_level]
