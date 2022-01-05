from django.utils.translation import gettext_lazy as _
from .entity_set import EntitySet
from ..entity_readers.user_reader import UserReader


class UserSet(EntitySet):
    """
    Represents list of all registered users and allows to facilitate the user lookup
    """

    _entity_name = _("User")

    _entity_class = "core.entity.user.User"

    _entity_reader_class = UserReader

    _entity_filter_list = {
        "login": [str, None],
        "group": ["core.entity.group.Group", None]
    }

    _alias_kwarg = "login"
    """ Defines the name of the field in Django model that is used for alias lookup by get('some_alias_string') """
