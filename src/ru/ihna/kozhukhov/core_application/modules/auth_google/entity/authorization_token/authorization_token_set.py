from .....entity.entity_sets.external_authorization_token_set import ExternalAuthorizationTokenSet

from .authorization_token_reader import AuthorizationTokenReader


class AuthorizationTokenSet(ExternalAuthorizationTokenSet):
    """
    Returns the token set.
    """

    _entity_name = "Google authorization token"

    _entity_reader_class = AuthorizationTokenReader
