from core.test.entity_set.external_accounts import TestExternalAccounts

from .account_set_object import AccountSetObject


class TestAccountSet(TestExternalAccounts):
    """
    Tests the set of external accounts
    """

    _external_account_set_object_class = AccountSetObject

    _no_filter_accounts = ["account0@mail.ru", "account10@mail.ru"]


del TestExternalAccounts
