from core.entity.external_authorization_token import ExternalAuthorizationToken
from core.entity.entity_fields import EntityField, ReadOnlyField


class AuthorizationToken(ExternalAuthorizationToken):
    """
    Defines the way how the authorization token will be temporarily saved on the server.

    This way doesn't imply permanent token save in the database.
    """

    _entity_provider_list = []  # TO-DO: define the authorization token receive

    _public_field_description = {
        "code": EntityField(str, description="Authorization code"),
        "access_token": ReadOnlyField(description="Access token"),
        "expires_in": ReadOnlyField(description="Token expiration date"),
        "refresh_token": ReadOnlyField(description="Refresh token"),
    }
