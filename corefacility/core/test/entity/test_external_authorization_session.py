from parameterized import parameterized

from core import App as CoreApp

from authorizations.google import App as GoogleApp
from authorizations.ihna import App as IhnaApp

from core.test.data_providers.field_value_providers import put_stages_in_provider
from .base_test_class import BaseTestClass
from .entity_objects.external_authorization_session_object import ExternalAuthorizationSessionObject
from .entity_field_mixins.password_mixin import PasswordMixin
from .entity_field_mixins.expiry_date_mixin import ExpiryDateMixin
from ...entity.entity_exceptions import EntityFieldInvalid


def authorization_module_provider():
    return put_stages_in_provider([
        (IhnaApp(), GoogleApp(), None),
        (CoreApp(), GoogleApp(), ValueError),
        (42, GoogleApp(), ValueError)
    ])


class TestExternalAuthorizationSession(ExpiryDateMixin, PasswordMixin, BaseTestClass):

    _entity_object_class = ExternalAuthorizationSessionObject

    @parameterized.expand(authorization_module_provider())
    def test_authorization_module(self, *args):
        self._test_field("authorization_module", *args, use_defaults=False)

    @parameterized.expand([
        (PasswordMixin.PASSWORD_TEST_INITIAL,),
        (PasswordMixin.PASSWORD_TEST_SET,),
    ])
    def test_session_key_positive(self, test_number):
        self._test_password("session_key", test_number)

    @parameterized.expand([
        (PasswordMixin.PASSWORD_TEST_CLEAR,),
    ])
    def test_session_key_negative(self, test_number):
        with self.assertRaises(EntityFieldInvalid, msg="The session key can be successfully cleared"):
            self._test_password("session_key", test_number)

    @parameterized.expand([(test_number,) for test_number in range(3)])
    def test_session_key_expiry_date(self, test_number):
        self._test_expiry_date("session_key_expiry_date", test_number)

    def _check_field_consistency(self, obj):
        self.assertEquals(obj.entity.authorization_module.uuid, obj.entity_fields['authorization_module'].uuid,
                          "Authorization module was not correctly retrieved during the reload")
        self.assertTrue(obj.entity.session_key.check(obj.entity_fields['session_key']),
                        "Session key was not correctly retrieved during the reload")
        self.assertFalse(obj.entity.session_key_expiry_date.is_expired(),
                         "Session key expiration date was not retrieved during the reload")

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertIsInstance(entity.authorization_module, GoogleApp,
                              "The authorization module was not transmitted correctly")
        self.__check_expiry_date(entity)

    def _check_default_change(self, entity):
        self.assertIsInstance(entity.authorization_module, IhnaApp,
                              "The authorization module was not changed correctly")

    def __check_expiry_date(self, entity):
        self.assertFalse(entity.session_key_expiry_date.is_expired(),
                         "The session key was suddenly expired")


del BaseTestClass
