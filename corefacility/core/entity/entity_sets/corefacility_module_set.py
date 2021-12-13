from django.utils.translation import gettext_lazy as _
from .entity_set import EntitySet


class CorefacilityModuleSet(EntitySet):
    """
    Provides a good way to navigate among different corefacility modules
    """

    _entity_name = _("Corefacility module")

    _entity_class = "core.entity.corefacility_module.CorefacilityModule"

    _entity_reader_class = None   # TO-DO: define a proper entity reader

    _entity_filter_list = {
        "uuid": [str, None],
        "parent_entry_point": ["core.entity.entry_point.EntryPoint", None],
        "alias": [str, None],
        "is_application": [bool, None],
        "is_enabled": [bool, None],
    }
