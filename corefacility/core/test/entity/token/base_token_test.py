from parameterized import parameterized

from core.entity.user import User
from core.entity.entity_exceptions import EntityFieldInvalid
from core.test.data_providers.field_value_providers import token_provider, base_expiry_date_provider

from ..base_test_class import BaseTestClass
from ..entity_field_mixins.expiry_date_mixin import ExpiryDateMixin
from ..entity_field_mixins.password_mixin import PasswordMixin
from ..entity_field_mixins.user_field_mixin import UserFieldMixin


class TestToken(UserFieldMixin, ExpiryDateMixin, PasswordMixin, BaseTestClass):
    """
    The base class for testing authentications and cookies
    """

    _entity_object_class = None
    """ An object for a testing entity """

    _initial_user = None
    _final_user = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._initial_user = User(login="sergei.kozhukhov")
        cls._final_user = User(login="vasily.ivanov")

        cls._initial_user.create()
        cls._final_user.create()

        cls._entity_object_class.define_default_kwarg("user", cls._initial_user)
        cls._entity_object_class.define_change_kwarg("user", cls._final_user)

    @parameterized.expand(token_provider())
    def test_token_hash(self, test_number):
        """
        Checks whether the token hash is retrieved correctly

        :param test_number: number of test from the token provider
        :return: nothing
        """
        self._test_password("token_hash", test_number)

    @parameterized.expand(base_expiry_date_provider())
    def test_expiry_date(self, test_number):
        """
        Tests the token expiration date

        :param test_number: the test number from the base_expiry_date_provider
        :return: nothing
        """
        self._test_expiry_date("expiration_date", test_number)

    def test_user_negative(self):
        """
        Tests whether recently created, not saved user can be assigned
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.reload_entity()
        sample_user = User(login="sample")
        with self.assertRaises((ValueError, EntityFieldInvalid, RuntimeError),
                               msg="Non-existent user was successfully attached to the authentication token"):
            obj.entity.user = sample_user
            obj.entity.update()

    def _check_default_fields(self, token):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param token: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertFalse(token.expiration_date.is_expired(), "The token was immediately expired")
        self.assertEquals(token.user.id, self._initial_user.id, "The token user didn't saved correctly")

    def _check_default_change(self, token):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param token: the entity to store
        :return: nothing
        """
        self.assertFalse(token.expiration_date.is_expired(), "The token was immediately expired")
        self.assertEquals(token.user.id, self._final_user.id, "The token user didn't save correctly")

    def _check_field_consistency(self, obj):
        """
        Checks that all object fields were retrieved correctly.

        :param obj: the authentication object
        :return: nothing
        """
        self.assertTrue(obj.entity.token_hash.check(obj.initial_password),
                        "The token password doesn't retrieved correctly")
        self.assertFalse(obj.entity.expiration_date.is_expired(), "The token was immediately expired")

        actual_user = obj.entity.user
        expected_user = obj.entity_fields['user']
        self.assertEquals(actual_user.id, expected_user.id, "The user ID was not retrieved correctly")
        self.assertEquals(actual_user.login, expected_user.login, "The user login was not retrieved  correctly")
        self.assertEquals(actual_user.name, expected_user.name, "The user name was not retrieved correctly")
        self.assertEquals(actual_user.surname, expected_user.surname, "The user surname was not retrieved correctly")


del BaseTestClass
