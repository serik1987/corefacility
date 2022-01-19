from core.entity.external_authorization_token import ExternalAuthorizationToken
from core.entity.entity_fields import ReadOnlyField

from .mock_provider import MockProvider


class AuthorizationToken(ExternalAuthorizationToken):
    """
    Defines the external authorization token and links to the way how the token can be retrieved.

    When successfully authorized on the institute website the user receives the authorization code.
    Such a code is sent to this module by the user. The following steps of this module is to connect
    to this external website in order to exchange the authorization code to authorization token and/or
    some user info assigned to his account here.
    """

    _entity_provider_list = [MockProvider()]

    _intermediate_field_description = {
        "email": ReadOnlyField(description="User's login on the ihna.ru website")
    }
