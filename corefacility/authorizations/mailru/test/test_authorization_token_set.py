from core.test.entity_set.base_external_authorization_token_set import TestExternalAuthorizationTokenSet
from authorizations.mailru.entity import AuthorizationTokenSet

from .authorization_token_set_object import AuthorizationTokenSetObject


class TestAuthorizationTokenSet(TestExternalAuthorizationTokenSet):
    """
    Tests the sets consisting from authorization tokens
    """

    _token_set_object_class = AuthorizationTokenSetObject

    _token_set_class = AuthorizationTokenSet

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.access_token, expected_entity.access_token,
                          msg + ". Access token was not loaded correctly.")
        self.assertEquals(actual_entity.expires_in, expected_entity.expires_in,
                          msg + ". Token expiration date was not loaded correctly.")
        self.assertEquals(actual_entity.refresh_token, expected_entity.refresh_token,
                          msg + ". The refresh token was not loaded correctly.")


del TestExternalAuthorizationTokenSet
