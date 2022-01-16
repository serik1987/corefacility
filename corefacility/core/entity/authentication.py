from core.models import Authentication as AuthenticationModel

from .token import Token
from .entity_sets.authentication_set import AuthenticationSet
from .entity_providers.model_providers.authentication_provider import AuthenticationProvider


class Authentication(Token):
    """
    Provides a single authentication object. Authentications are used to generate
    tokens and restore active session using tokens
    """

    _entity_set_class = AuthenticationSet

    _token_model = AuthenticationModel

    _entity_provider_list = [AuthenticationProvider()]
