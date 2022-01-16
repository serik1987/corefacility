from datetime import timedelta

from core.entity.authentication import Authentication

from .token_object import TokenObject


class AuthenticationObject(TokenObject):
    """
    Contains routines that facilitate creating test authentications
    """

    _entity_class = Authentication
