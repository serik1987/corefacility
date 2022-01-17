from core.test.entity_set.entity_set_objects.external_account_set_object import ExternalAccountSetObject
from authorizations.google.entity import Account


class AccountSetObject(ExternalAccountSetObject):
    """
    This is the base class for all external account sets
    """

    _entity_class = Account
    _alias_field = "email"

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        return [
            dict(email="account0@gmail.com", user=self._user_set_object[0]),
            dict(email="account1@gmail.com", user=self._user_set_object[2]),
            dict(email="account2@gmail.com", user=self._user_set_object[4]),
            dict(email="account3@gmail.com", user=self._user_set_object[6]),
            dict(email="account4@gmail.com", user=self._user_set_object[8]),
        ]
