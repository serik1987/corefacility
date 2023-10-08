from .model_provider import ModelProvider
from .authentication_provider import AuthenticationProvider


class ExternalAuthorizationTokenProvider(ModelProvider):
    """
    The ExternalAuthorizationTokenProvider is responsible for storing the external authorization token to the
    database and conversion of the external authorization token from Django model or its emulator to
    the Entity instance
    """

    _authentication_provider = AuthenticationProvider()

    def wrap_entity(self, external_object):
        entity = super().wrap_entity(external_object)
        entity._authentication = self._authentication_provider.wrap_entity(entity._authentication)
        return entity
