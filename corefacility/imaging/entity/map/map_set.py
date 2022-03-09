from django.utils.translation import gettext_lazy as _

from core.entity.entity_sets.entity_set import EntitySet

from .map_reader import MapReader


class MapSet(EntitySet):
    """
    Represents a set or imaging maps each of which can be retrieved from the database
    """

    _entity_reader_class = MapReader

    _entity_name = _("Functional map")
