from core.entity.external_authorization_token import ExternalAuthorizationToken
from core.entity.entity_fields import ReadOnlyField, ManagedEntityField

from .authorization_token_set import AuthorizationTokenSet
from .model_provider import ModelProvider
from .mock_provider import MockProvider
from .refresh_token_manager import RefreshTokenManager


class AuthorizationToken(ExternalAuthorizationToken):
    """
    Defines the Google external authorization token and the ways
    how the token can be received, stored or retrieved

    Let's mention all public fields and how the ExternalAuthorizationToken works:

    * code - when you gave the authorization code from the user you need to fill in this field
    by putting the code to this field, like here: token = AuthorizationToken(code=your_authorization_code)
    When you call token.create() the entity will make the first request to Google to exchange the authorization
    code to the authorization token. Next, it make the second request to Google to receive the user's account name
    using the authorization token. Third, the entity will query the Account entity to find the user with
    particular account name. And at last the entity will save all the data received from Google and the Account
    entity to the database. When the entity is loaded from the local database the value of this field is None which
    means that you are no longer need the authorization code. The field is required when you create() an entity
    but the field is not required when you update() the entity.

    * access_token - this is a read-only field. Before creating an instance the field value is None while
    after its create the field value is a particular access token.

    * expires_in - just informative field that allows you to check whether the access token is expired

    * refresh_token - the token is required to refresh the access token when this is expired. To refresh the
    access_token just use the following: token.refresh_token.refresh(). This will request the Google for new
    access token and updated the newly created access token to the database.

    * authentication - the authentication attached to the token. In order to look the user this token belongs to
    use: token.authentication.user.
    """

    _entity_set_class = AuthorizationTokenSet

    _entity_provider_list = [MockProvider(), ModelProvider()]

    _intermediate_field_description = {
        "access_token": ReadOnlyField(description="Access token"),
        "expires_in": ReadOnlyField(description="Access token expiration time"),
        "refresh_token": ManagedEntityField(RefreshTokenManager, description="Refresh token")
    }
