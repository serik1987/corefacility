from parameterized import parameterized

from core.entity.user import User
from core.entity.entity_exceptions import EntityDuplicatedException
from core.test.entity.base_external_authorization_account import TestExternalAuthorizationAccount
from core.test.data_providers.field_value_providers import string_provider
from authorizations.google.entity import Account

from .account_object import AccountObject


class TestAccount(TestExternalAuthorizationAccount):
    """
    Tests the Google account
    """

    _entity_object_class = AccountObject

    _user_test_additional_kwargs = {
        "email": "serik1987@gmail.com",
    }

    @parameterized.expand(string_provider(1, 254))
    def test_email(self, *args):
        self._test_field("email", *args, use_defaults=False, user=self._sample_user)

    def test_email_uniqueness(self):
        another_user = User(login="vasily.petrov")
        another_user.create()
        account1 = Account(email="serik1987@gmail.com", user=self._sample_user)
        account1.create()
        account2 = Account(email="serik1987@gmail.com", user=another_user)
        with self.assertRaises(EntityDuplicatedException,
                               msg="The same Google account may belong to two or more users"):
            account2.create()

    def _check_default_fields(self, account):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param account: the entity which default fields shall be checked
        :return: nothing
        """
        self._check_user_fields(account)
        self.assertEquals(account.email, "serik1987@gmail.com",
                          "The account e-mail was lost")

    def _check_default_change(self, account):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param account: the entity to store
        :return: nothing
        """
        self._check_user_fields(account)
        self.assertEquals(account.email, "kozhukhov@gmail.com",
                          "The account e-mail was not changed correctly")


del TestExternalAuthorizationAccount
