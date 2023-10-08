from parameterized import parameterized

from ....exceptions.entity_exceptions import EntityDuplicatedException
from ....test.entity.base_external_authorization_account import TestExternalAuthorizationAccount
from ....test.data_providers.field_value_providers import string_provider
from ..entity import Account

from .account_object import AccountObject


class TestAccount(TestExternalAuthorizationAccount):
    """
    Tests the account for being read or write properly
    """

    _entity_object_class = AccountObject

    _user_test_additional_kwargs = {"email": "sergei.kozhukhov@ihna.ru"}

    @parameterized.expand(string_provider(1, 254))
    def test_email(self, *args):
        self._test_field("email", *args, use_defaults=False, user=self._sample_user)

    def test_email_uniqueness(self):
        account1 = Account(user=self._sample_user, email="example@mail.ru")
        account1.create()

        account2 = Account(user=self._sample_user, email="example@mail.ru")
        with self.assertRaises(EntityDuplicatedException, msg="The duplicated entity was successfully created"):
            account2.create()

    def _check_default_fields(self, account):
        self._check_user_fields(account)
        self.assertEquals(account.email, "sergei.kozhukhov@ihna.ru",
                          "The account e-mail was not transmitted successfully")

    def _check_default_change(self, account):
        self._check_user_fields(account)
        self.assertEquals(account.email, "sergeykozh@mail.ru",
                          "The account e-mail was not changed successfully")


del TestExternalAuthorizationAccount
