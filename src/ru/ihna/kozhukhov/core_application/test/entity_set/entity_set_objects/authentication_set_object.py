from ru.ihna.kozhukhov.core_application.entity.authentication import Authentication

from .token_set_object import TokenSetObject


class AuthenticationSetObject(TokenSetObject):
    """
    Contains a set of test authentication records
    """

    _entity_class = Authentication
