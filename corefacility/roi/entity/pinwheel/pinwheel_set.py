from django.utils.translation import gettext_lazy as _

from core.entity.entity_exceptions import EntityNotFoundException
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
        "map_id": (int, None),
        "map_alias": (str, None),
        "project_id": (int, None),
    }

    def get(self, lookup):
        """
        Finds the entity by id or alias
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity alias is a unique string name assigned by the user during the entity post.

        The function must be executed in one request

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        if isinstance(lookup, str):
            raise EntityNotFoundException()
        return super().get(lookup)
