from django.utils.translation import gettext_lazy as _
from .entity_set import EntitySet
from core.entity.entity import Entity


class GroupSet(EntitySet):
    """
    Manages different groups and allows searching among them
    """

    _entity_name = _("Scientific Group")

    _entity_class = "core.entity.group.Group"

    _entity_reader_class = None  # TO-DO: Define and implement a proper group reader

    _entity_filter_list = {
        "name": [str, None],
        "user": ["core.entity.user.User", lambda user: user.login != "support"]
    }
