from core.test.entity_set.entity_set_objects.external_authorization_token_set_object import \
    ExternalAuthorizationTokenSetObject
from authorizations.google.entity import AuthorizationToken


class AuthorizationTokenSetObject(ExternalAuthorizationTokenSetObject):
    """
    Creates a list of sample authorization tokens and manages such a list.
    """

    _entity_class = AuthorizationToken
