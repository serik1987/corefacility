from core.test.entity_set.external_accounts import TestExternalAccounts

from .account_set_object import AccountSetObject


class TestAccountSet(TestExternalAccounts):
    """
    Executes standard test routines for the IHNA account set
    """

    _external_account_set_object_class = AccountSetObject

    _no_filter_accounts = ["account0@ihna.ru", "account20@ihna.ru"]


del TestExternalAccounts
