from django.utils.translation import gettext_lazy as _

from core.entity.entity_sets.entity_set import EntitySet

from .pinwheel_reader import PinwheelReader


class PinwheelSet(EntitySet):
    """
    Represents a 'virtual container' where all pinwheels are stored.
    Also, provides searching facilities across pinwheels.
    """

    _entity_name = _("Pinwheel")

    _entity_reader_class = PinwheelReader

    _entity_filter_list = {
        "map": ("imaging.entity.Map", None),
    }
