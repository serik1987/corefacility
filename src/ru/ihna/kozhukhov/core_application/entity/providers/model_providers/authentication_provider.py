from ....models import Authentication as AuthenticationModel

from .token_provider import TokenProvider


class AuthenticationProvider(TokenProvider):
    """
    Launches the authentication provider.
    """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.authentication.Authentication"
    _entity_model = AuthenticationModel
