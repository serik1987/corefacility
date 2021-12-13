from django.utils.translation import gettext_lazy as _
from .permission_set import PermissionSet


class AppPermissionSet(PermissionSet):
    """
    Defines some application permission
    """

    _entity_name = _("Application permission")

    _entity_class = "core.entity.application_permission.ApplicationPermission"

    _entity_reader_class = None   # TO-DO: define a proper entity reader

    _entity_filter_list = {
        "entity": ["core.entity.corefacility_module.CorefacilityModule", lambda module: module.is_application()]
    }
