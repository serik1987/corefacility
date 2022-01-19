from core.entity.external_authorization_token import ExternalAuthorizationToken
from core.entity.entity_fields import ReadOnlyField, ManagedEntityField

from .authorization_token_set import AuthorizationTokenSet
from .mock_provider import MockProvider
from .model_provider import ModelProvider
from .refresh_token import RefreshTokenManager


class AuthorizationToken(ExternalAuthorizationToken):
    """
    Defines the way how the authorization token will be temporarily saved on the server.

    This way doesn't imply permanent token save in the database.
    """

    _entity_set_class = AuthorizationTokenSet

    _entity_provider_list = [MockProvider(), ModelProvider()]

    _intermediate_field_description = {
        "access_token": ReadOnlyField(description="Access token"),
        "expires_in": ReadOnlyField(description="Token expiration date"),
        "refresh_token": ManagedEntityField(RefreshTokenManager,
                                            description="Refresh token")
    }
