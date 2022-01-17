from core.test.entity_set.external_accounts import TestExternalAccounts

from .account_set_object import AccountSetObject


class TestAccountSet(TestExternalAccounts):

    _external_account_set_object_class = AccountSetObject

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.email, expected_entity.email, msg="Account E-mail is not the same as expected")


del TestExternalAccounts
