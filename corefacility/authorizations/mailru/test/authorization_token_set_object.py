from core.test.entity_set.entity_set_objects.external_authorization_token_set_object \
    import ExternalAuthorizationTokenSetObject
from authorizations.mailru.entity import AuthorizationToken


class AuthorizationTokenSetObject(ExternalAuthorizationTokenSetObject):
    """
    Creates a testing external authorization sets
    """

    _entity_class = AuthorizationToken
