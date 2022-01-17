from parameterized import parameterized

from core.entity.user import User
from core.entity.entity_exceptions import EntityDuplicatedException
from core.test.entity.base_external_authorization_account import TestExternalAuthorizationAccount
from core.test.data_providers.field_value_providers import string_provider
from authorizations.ihna.entity import Account

from .account_object import AccountObject


class TestAccount(TestExternalAuthorizationAccount):

    _entity_object_class = AccountObject

    _user_test_additional_kwargs = {
        "email": "example@ihna.ru"
    }

    @parameterized.expand(string_provider(1, 254))
    def test_email(self, *args):
        self._test_field("email", *args, use_defaults=False, user=self._sample_user)

    def test_email_uniqueness(self):
        account1 = Account(email="sergei.kozhukhov@ihna.ru", user=self._sample_user)
        account1.create()

        another_user = User(login="iii", name="Vasya", surname="Pupkin")
        another_user.create()

        with self.assertRaises(EntityDuplicatedException,
                               msg="The IHNA account was successfully attached to two different users"):
            account2 = Account(email="sergei.kozhukhov@ihna.ru", user=self._sample_user)
            account2.create()

    def _check_default_fields(self, account):
        self.assertEquals(account.email, "sergei.kozhukhov@ihna.ru",
                          "The default account e-mail was not correctly transmitted")
        self._check_user_fields(account)

    def _check_default_change(self, account):
        self.assertEquals(account.email, "ivan.ivanov@ihna.ru",
                          "The account e-mail was not correctly changed")
        self._check_user_fields(account)


del TestExternalAuthorizationAccount
