from core.entity.entity_providers.model_providers.external_authorization_token_provider import \
    ExternalAuthorizationTokenProvider
from authorizations.google.models import AuthorizationToken as AuthorizationTokenModel


class ModelProvider(ExternalAuthorizationTokenProvider):
    """
    The model provider always execute after the RemoteServerProvider receives the authorization token and
    all its related account details from the Google server and is responsible to exchange such information
    between the AuthorizationToken entity and the database
    """

    _entity_model = AuthorizationTokenModel

    _lookup_field = "id"

    _model_fields = ["access_token", "expires_in", "refresh_token", "authentication"]

    _entity_class = "authorizations.google.entity.AuthorizationToken"
