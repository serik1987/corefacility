from core.entity.external_authorization_token import ExternalAuthorizationToken
from core.entity.entity_fields import EntityField, ReadOnlyField


class AuthorizationToken(ExternalAuthorizationToken):
    """
    Defines the Google external authorization token and the ways
    how the token can be received, stored or retrieved
    """

    _entity_provider_list = []  # TO-DO: Define proper entity providers

    _public_field_description = {
        "code": EntityField(str, description="Authorization code"),
        "access_token": ReadOnlyField(description="Access token"),
        "expires_in": ReadOnlyField(description="Access token expiration time"),
        "refresh_token": ReadOnlyField(description="Refresh token"),
        "authentication": ReadOnlyField(description="Related user authentication"),
    }
