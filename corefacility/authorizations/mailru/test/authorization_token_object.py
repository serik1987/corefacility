from core.test.entity.entity_objects.external_authorization_token_object import ExternalAuthorizationTokenObject
from authorizations.mailru.entity import AuthorizationToken


class AuthorizationTokenObject(ExternalAuthorizationTokenObject):
    """
    Facilitates creating, updating, reading or deleting test authorization tokens
    """

    _entity_class = AuthorizationToken

    def change_entity_fields(self, use_defaults=True, **kwargs):
        self.entity.refresh_token.refresh()
