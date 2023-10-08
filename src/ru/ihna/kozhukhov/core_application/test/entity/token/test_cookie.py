from .base_token_test import TestToken
from ..entity_objects.cookie_object import CookieObject


class TestCookie(TestToken):
    """
    Implements the cookie test routines
    """

    _entity_object_class = CookieObject
    """ An object for a testing entity """


del TestToken
