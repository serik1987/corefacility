from django.utils.translation import gettext_lazy as _
from .permission_set import PermissionSet


class ProjectPermissionSet(PermissionSet):
    """
    Defines some project permission
    """

    _entity_name = _("Project permission")

    _entity_class = "core.entity.project_permission.ProjectPermission"

    _entity_reader_class = None  # TO-DO: define a proper entity reader

    _entity_filter_list = {
        "entity": ["core.entity.project.Project", None]
    }
