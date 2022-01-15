from core.models import Authentication as AuthenticationModel
from core.entity.entity_providers.model_providers.authentication_provider import AuthenticationProvider

from .model_reader import ModelReader


class AuthenticationReader(ModelReader):
    """
    Reads the authentications from the database
    """

    _entity_model_class = AuthenticationModel
    _entity_provider = AuthenticationProvider()
