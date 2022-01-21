from django.utils.translation import gettext_lazy as _

from .entity_set import EntitySet
from ..entity_readers.corefacility_module_reader import CorefacilityModuleReader


class CorefacilityModuleSet(EntitySet):
    """
    Provides a good way to navigate among different corefacility modules
    """

    _entity_name = _("Corefacility module")

    _entity_class = "core.entity.corefacility_module.CorefacilityModule"

    _entity_reader_class = CorefacilityModuleReader

    _entity_filter_list = {
        "entry_point_alias": [str, None],
    }
