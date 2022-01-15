from time import sleep
from datetime import timedelta
from parameterized import parameterized

from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.authentication import Authentication
from core.entity.entity_sets.authentication_set import AuthenticationSet

from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.authentication_set_object import AuthenticationSetObject


def authentication_reading_provider():
    return [
        (0, 0),
        (1, 0),
        (2, 3),
    ]


class TestAuthenticationSet(BaseTestClass):
    """
    Tests the authentication set
    """

    TEST_EXPIRY_TERM = timedelta(milliseconds=300)

    _user_set_object = None
    _authentication_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._authentication_set_object = AuthenticationSetObject(cls._user_set_object)

    @parameterized.expand(authentication_reading_provider())
    def test_authentication_retrieve(self, auth_index, user_index):
        auth_id = self._authentication_set_object[auth_index].id
        desired_user = self._user_set_object[user_index]
        auth_set = AuthenticationSet()
        with self.assertLessQueries(1):
            auth = auth_set.get(auth_id)
        self.assertAuthenticationUser(auth.user, desired_user)

    def test_high_level_positive(self):
        user = self._user_set_object[0]
        token = Authentication.new_authentication(user, self.TEST_EXPIRY_TERM)
        Authentication.authenticate(token)
        self.assertAuthenticationUser(Authentication.get_user(), user)

    def test_high_level_expired(self):
        user = self._user_set_object[0]
        token = Authentication.new_authentication(user, self.TEST_EXPIRY_TERM)
        sleep(self.TEST_EXPIRY_TERM.total_seconds())
        with self.assertRaises(EntityNotFoundException, msg="The token can't be expired within the expiration time"):
            Authentication.authenticate(token)

    def assertAuthenticationUser(self, actual_user, desired_user):
        self.assertEquals(actual_user.id, desired_user.id, "The desired user was not loaded correctly")
        self.assertEquals(actual_user.login, desired_user.login, "The desired user login was not loaded correctly")
        self.assertEquals(actual_user.name, desired_user.name, "The desired user name was not loaded correctly")
        self.assertEquals(actual_user.surname, desired_user.surname,
                          "The desired user surname was not loaded correctly")
