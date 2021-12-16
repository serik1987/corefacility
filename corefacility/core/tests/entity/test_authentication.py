from datetime import timedelta
from time import sleep

from parameterized import parameterized_class

from core.entity.entity_exceptions import EntityFieldInvalid, EntityNotFoundException
from core.entity.entity_fields import EntityPasswordManager
from core.tests.entity.entity import EntityTest
from core.tests.entity.entity_providers.dump_entity_provider import DumpAuthentication, DumpUser, DumpEntityProvider


@parameterized_class([
    {
        "entity_name": DumpAuthentication,
        "user_name": DumpUser,
    }
])
class TestAuthentication(EntityTest):

    test_user = None
    another_user = None

    def setUp(self):
        super().setUp()
        self.test_user = self.user_name(login="test123")
        self.test_user.create()
        self.another_user = self.user_name(login="test456")
        self.another_user.create()

    def test_incorrect_user_assignment(self):
        authentication = self._create_demo_entity()
        authentication.create()
        with self.assertRaises(ValueError, msg="Invalid user was assigned to the authentication token"):
            authentication.user = "Vovan"
            authentication.update()

    def test_password_field(self):
        self._test_password_field("token_hash")

    def test_expiry_date_field(self):
        self._test_expiry_date_field("expiration_date")

    def test_user_not_defined(self):
        authentication = self.entity_name()
        authentication.token_hash.generate(EntityPasswordManager.ALL_SYMBOLS, 20)
        authentication.expiration_date.set(timedelta(seconds=1))
        self.assert_no_create(authentication, "user")

    def test_token_not_defined(self):
        authentication = self.entity_name(
            user=self.test_user
        )
        authentication.expiration_date.set(timedelta(seconds=1))
        self.assert_no_create(authentication, "token_hash")

    def test_expiration_date_not_defined(self):
        authentication = self.entity_name(
            user=self.test_user
        )
        authentication.token_hash.generate(EntityPasswordManager.ALL_SYMBOLS, 20)
        self.assert_no_create(authentication, "expiration_date")

    def test_authentication_process(self):
        token = self.entity_name.new_authentication(self.test_user, timedelta(seconds=1))
        self.assertIsNone(self.entity_name.get_user(),
                          msg="The user is self-authenticated when authentication is created")
        self.entity_name.authenticate(token)
        self.assertEquals(self.entity_name.get_user(), self.test_user, "Failed to recover the authorization session")
        with self.assertRaises(EntityNotFoundException, msg="Authenticated using invalid token"):
            self.entity_name.authenticate("MTohP2l0cGkwLlYrJ2RDXkFJKjx0QA==")
        sleep(1)
        with self.assertRaises(EntityNotFoundException, msg="Authenticated using expired token"):
            self.entity_name.authenticate(token)

    def assert_no_create(self, authentication, field_name):
        with self.assertRaises(EntityFieldInvalid,
                               msg="Authentication with no '%s' field being filled was created" % field_name):
            authentication.create()

    def _create_demo_entity(self):
        authentication = self.entity_name(
            user=self.test_user
        )
        authentication.token_hash.generate(EntityPasswordManager.ALL_SYMBOLS, 20)
        authentication.expiration_date.set(timedelta(seconds=1))
        return authentication

    def _update_demo_entity(self, entity):
        entity.user = self.another_user


del TestAuthentication
del EntityTest
