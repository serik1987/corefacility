from core.test.entity_set.entity_set_objects.external_account_set_object import ExternalAccountSetObject
from authorizations.mailru.entity import Account


class AccountSetObject(ExternalAccountSetObject):
    """
    A set of external account objects.
    """

    _entity_class = Account

    _alias_field = "email"

    def data_provider(self):
        return [
            dict(user=self._user_set_object[0], email="account0@mail.ru"),
            dict(user=self._user_set_object[2], email="account1@mail.ru"),
            dict(user=self._user_set_object[4], email="account2@mail.ru"),
            dict(user=self._user_set_object[6], email="account3@mail.ru"),
            dict(user=self._user_set_object[8], email="account4@mail.ru"),
        ]
