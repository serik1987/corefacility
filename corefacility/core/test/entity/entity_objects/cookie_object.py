from authorizations.cookie.entity import Cookie

from .token_object import TokenObject


class CookieObject(TokenObject):
    """
    Contains routines that facilitate creating of cookie objects
    """

    _entity_class = Cookie
