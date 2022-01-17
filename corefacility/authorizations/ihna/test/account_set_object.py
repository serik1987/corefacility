from core.test.entity_set.entity_set_objects.external_account_set_object import ExternalAccountSetObject
from authorizations.ihna.entity import Account


class AccountSetObject(ExternalAccountSetObject):
    
    _entity_class = Account

    _alias_field = "email"

    def data_provider(self):
        return [
            dict(email="account0@ihna.ru", user=self._user_set_object[0]),
            dict(email="account1@ihna.ru", user=self._user_set_object[2]),
            dict(email="account2@ihna.ru", user=self._user_set_object[4]),
            dict(email="account3@ihna.ru", user=self._user_set_object[6]),
            dict(email="account4@ihna.ru", user=self._user_set_object[8]),
        ]
