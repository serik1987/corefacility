from django.utils.translation import gettext_lazy as _
from .entity_set import EntitySet
from ..readers.group_reader import GroupReader


class GroupSet(EntitySet):
    """
    Manages different groups and allows searching among them
    """

    _entity_name = _("Scientific Group")

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.group.Group"

    _entity_reader_class = GroupReader

    _entity_filter_list = {
        "name": [str, None],
        "user": ["ru.ihna.kozhukhov.core_application.entity.user.User", lambda user: user.login != "support"],
        "governor": ["ru.ihna.kozhukhov.core_application.entity.user.User", lambda user: user.login != "support"]
    }
