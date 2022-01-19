from core.entity.entity_sets.external_authorization_token_set import ExternalAuthorizationTokenSet

from .authorization_token_reader import AuthorizationTokenReader


class AuthorizationTokenSet(ExternalAuthorizationTokenSet):
    """
    Allows to find proper authorization token within the token set.
    """

    _entity_name = "Mail.Ru authorization token"

    _entity_reader_class = AuthorizationTokenReader
