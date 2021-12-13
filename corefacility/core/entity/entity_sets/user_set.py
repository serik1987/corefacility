from django.utils.translation import gettext_lazy as _
from .entity_set import EntitySet


class UserSet(EntitySet):
    """
    Represents list of all registered users and allows to facilitate the user lookup
    """

    _entity_name = _("User")

    _entity_class = "core.entity.user.User"

    _entity_reade_class = None  # TO-DO: create new entity reader for this user

    _entity_filter_list = {
        "login": [str, None],
        "group": ["core.entity.group.Group", None]
    }
