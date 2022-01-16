from authorizations.cookie.entity import Cookie

from .token_set_object import TokenSetObject


class CookieSetObject(TokenSetObject):
    """
    Contains a set of token testing records.
    """

    _entity_class = Cookie
