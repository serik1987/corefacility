from time import sleep
from datetime import timedelta
from parameterized import parameterized

from core.entity.entity_exceptions import EntityNotFoundException

from ..base_test_class import BaseTestClass
from ..entity_set_objects.user_set_object import UserSetObject


def token_reading_provider():
    return [
        (0, 0),
        (1, 0),
        (2, 3),
    ]


class TokenTest(BaseTestClass):
    """
    The base class for testing all internally issued tokens (i.e., authentications, cookies etc.)
    """

    TEST_EXPIRY_TERM = timedelta(milliseconds=300)

    _token_set_class = None
    _token_class = None
    _token_object_class = None

    _user_set_object = None
    _token_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._authentication_set_object = cls._token_object_class(cls._user_set_object)

    @parameterized.expand(token_reading_provider())
    def test_authentication_retrieve(self, auth_index, user_index):
        auth_id = self._authentication_set_object[auth_index].id
        desired_user = self._user_set_object[user_index]
        auth_set = self._token_set_class()
        with self.assertLessQueries(1):
            auth = auth_set.get(auth_id)
        self.assertTokenUser(auth.user, desired_user)

    def test_high_level_positive(self):
        user = self._user_set_object[0]
        token = self._token_class.issue(user, self.TEST_EXPIRY_TERM)
        self._token_class.apply(token)
        self.assertTokenUser(self._token_class.get_user(), user)

    def test_high_level_expired(self):
        user = self._user_set_object[0]
        token = self._token_class.issue(user, self.TEST_EXPIRY_TERM)
        sleep(self.TEST_EXPIRY_TERM.total_seconds())
        with self.assertRaises(EntityNotFoundException, msg="The token can't be expired within the expiration time"):
            self._token_class.apply(token)

    def test_clear_all_authentications_positive(self):
        user = self._user_set_object[0]
        token = self._token_class.issue(user, self.TEST_EXPIRY_TERM)
        self._token_class.clear_all_expired_tokens()
        self._token_class.apply(token)

    def test_clear_all_authentications_negative(self):
        user = self._user_set_object[0]
        auth = self._token_class(user=user)
        auth.token_hash.generate(auth.token_hash.ALL_SYMBOLS, auth.TOKEN_PASSWORD_SIZE)
        auth.expiration_date.set(self.TEST_EXPIRY_TERM)
        auth.create()
        sleep(self.TEST_EXPIRY_TERM.total_seconds() * 10)
        self._token_class.clear_all_expired_tokens()
        auth_set = self._token_set_class()
        with self.assertRaises(EntityNotFoundException, msg="The expired tokens were not carefully cleared"):
            auth_set.get(auth.id)

    def assertTokenUser(self, actual_user, desired_user):
        self.assertEquals(actual_user.id, desired_user.id, "The desired user was not loaded correctly")
        self.assertEquals(actual_user.login, desired_user.login, "The desired user login was not loaded correctly")
        self.assertEquals(actual_user.name, desired_user.name, "The desired user name was not loaded correctly")
        self.assertEquals(actual_user.surname, desired_user.surname,
                          "The desired user surname was not loaded correctly")


del BaseTestClass
