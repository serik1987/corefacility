from ....entity.entity_sets.entity_set import EntitySet

from .cookie_reader import CookieReader


class CookieSet(EntitySet):
    """
    Defines the cookie set and help to find a particular cookie in the database
    """

    _entity_name = "Cookie info"

    _entity_class = "ru.ihna.kozhukhov.core_application.modules.auth_cookie.entity.Cookie"

    _entity_reader_class = CookieReader

    _entity_filter_list = {}
