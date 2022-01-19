from core.entity.entity_providers.model_providers.external_authorization_token_provider import \
    ExternalAuthorizationTokenProvider
from authorizations.mailru.models import AuthorizationToken


class ModelProvider(ExternalAuthorizationTokenProvider):
    """
    Exchanges the authorization token information between the AuthorizationToken entity and
    the AuthorizationToken model.

    The class is responsible for interface negotiation and transformation of the data format.
    """

    _entity_class = "authorizations.mailru.entity.AuthorizationToken"

    _entity_model = AuthorizationToken
    
    _lookup_field = "id"

    _model_fields = ["access_token", "expires_in", "refresh_token", "authentication"]
