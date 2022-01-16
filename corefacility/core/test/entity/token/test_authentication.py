from .base_token_test import TestToken
from ..entity_objects.authentication_object import AuthenticationObject


class TestAuthentication(TestToken):
    """
    Implements the authentication test routines
    """

    _entity_object_class = AuthenticationObject
    """ An object for a testing entity """


del TestToken
