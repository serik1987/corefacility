from core.test.entity.entity_objects.external_authorization_token_object import \
    ExternalAuthorizationTokenObject
from authorizations.google.entity import AuthorizationToken


class AuthorizationTokenObject(ExternalAuthorizationTokenObject):
    """
    Facilitates using AuthorizationToken for the testing purpose.
    """

    _entity_class = AuthorizationToken

    def create_entity(self):
        super().create_entity()
        self._entity_fields['access_token'] = self.entity.access_token
        self._entity_fields['expires_in'] = self.entity.expires_in
        self._entity_fields['refresh_token'] = self.entity.refresh_token

    def change_entity_fields(self, use_defaults=True, **kwargs):
        self.entity.refresh_token.refresh()

    def notify_access_token_changed(self):
        self._entity_fields['access_token'] = self.entity.access_token
        self._entity_fields['expires_in'] = self.entity.expires_in
