from ....entity.authentication import Authentication
from ....entity.entity_sets.authentication_set import AuthenticationSet

from .base_test_class import TokenTest
from ..entity_set_objects.authentication_set_object import AuthenticationSetObject


class TestAuthenticationSet(TokenTest):
    """
    Tests the authentication set
    """

    _token_set_class = AuthenticationSet
    _token_class = Authentication
    _token_object_class = AuthenticationSetObject


del TokenTest
