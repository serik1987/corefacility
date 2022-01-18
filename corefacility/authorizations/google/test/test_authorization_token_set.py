from core.test.entity_set.base_external_authorization_token_set import TestExternalAuthorizationTokenSet
from authorizations.google.entity import AuthorizationTokenSet

from .authorization_token_set_object import AuthorizationTokenSetObject


class TestAuthorizationTokenSet(TestExternalAuthorizationTokenSet):
    """
    Tests the authorization token set
    """

    _token_set_object_class = AuthorizationTokenSetObject
    _token_set_class = AuthorizationTokenSet

    def assertEntityFound(self, actual, expected, msg):
        super().assertEntityFound(actual, expected, msg)
        self.assertEquals(actual.access_token, expected.access_token,
                          msg + ". Access tokens are not the same")
        self.assertEquals(actual.expires_in, expected.expires_in,
                          msg + ". Token expiration dates are not the same")
        self.assertEquals(actual.refresh_token, expected.refresh_token,
                          msg + ". Refresh tokens are not the same")


del TestExternalAuthorizationTokenSet
