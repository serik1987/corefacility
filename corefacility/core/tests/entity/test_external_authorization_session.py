from datetime import timedelta
from time import sleep

from authorizations.google import App as AuthorizationModule
from authorizations.mailru import App as AnotherAuthorizationModule
from django.test import TestCase
from parameterized import parameterized_class, parameterized

from core.entity.entity_exceptions import EntityNotFoundException
from core.tests.entity.entity_providers.dump_entity_provider import DumpEntityProvider, DumpExternalAuthorizationSession

EMPTY_SESSION_TOKEN = ""
INVALID_SESSION_TOKEN = "MTovT1NqcD1ZVWt6"


@parameterized_class([
    {
        "session_class": DumpExternalAuthorizationSession
    }
])
class TestExternalAuthorizationSession(TestCase):

    _auth_module = None
    _another_auth_module = None

    def setUp(self):
        DumpEntityProvider.clear_entity_field_cache()
        self._auth_module = AuthorizationModule()
        self._another_auth_module = AnotherAuthorizationModule()
        if self.session_class == DumpExternalAuthorizationSession:
            self._auth_module._id = 0
            self._another_auth_module._id = 0

    def test_normal_session_restoration(self):
        session_token = self.session_class.initialize(self._auth_module, timedelta(seconds=1))
        self.session_class.restore(self._auth_module, session_token)

    def test_incorrect_module(self):
        session_token = self.session_class.initialize(self._auth_module, timedelta(seconds=1))
        with self.assertRaises(EntityNotFoundException,
                               msg="External authorization session restored using session key "
                                   "issued by another module"):
            self.session_class.restore(self._another_auth_module, session_token)

    @parameterized.expand([EMPTY_SESSION_TOKEN, INVALID_SESSION_TOKEN])
    def test_invalid_session_key(self, session_key):
        self.session_class.initialize(self._auth_module, timedelta(seconds=1))
        with self.assertRaises(EntityNotFoundException,
                               msg="External authorization session restored using invalid session key"):
            self.session_class.restore(self._auth_module, session_key)

    def test_expired_session_key(self):
        session_key = self.session_class.initialize(self._auth_module, timedelta(seconds=1))
        sleep(1)
        with self.assertRaises(EntityNotFoundException,
                               msg="Expired external authorization token has been successfully passed"):
            self.session_class.restore(self._auth_module, session_key)

    def test_double_authorization(self):
        session_key = self.session_class.initialize(self._auth_module, timedelta(seconds=1))
        self.session_class.restore(self._auth_module, session_key)
        with self.assertRaises(EntityNotFoundException,
                               msg="The software tester applied the same session key twice"):
            self.session_class.restore(self._auth_module, session_key)
