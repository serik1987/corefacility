from authorizations.cookie.entity import Cookie, CookieSet

from .base_test_class import TokenTest
from ..entity_set_objects.cookie_set_object import CookieSetObject


class TestCookie(TokenTest):
    """
    Tests the cookie record
    """

    _token_class = Cookie
    _token_set_class = CookieSet
    _token_object_class = CookieSetObject


del TokenTest
