from datetime import timedelta

from .entity_set_object import EntitySetObject


class TokenSetObject(EntitySetObject):
    """
    Prepares the entity sets for various kinds of tokens (i.e., authentications, cookie tokens etc.)
    """

    TOTAL_SYMBOLS = 20
    EXPIRY_TERM = timedelta(milliseconds=400)

    _entity_class = None

    _token_passwords = None

    def __init__(self, user_set_object, _entity_list=None):
        if len(user_set_object) < 4:
            raise RuntimeError("Please, provide user_set_object containing at least four users")
        if _entity_list is not None:
            self._entities = _entity_list
        else:
            self._entities = []
            self._token_passwords = []
            for user_index in self.data_provider():
                user = user_set_object[user_index]
                authentication = self._entity_class(user=user)
                password = authentication.token_hash.generate(authentication.token_hash.ALL_SYMBOLS, self.TOTAL_SYMBOLS)
                authentication.expiration_date.set(self.EXPIRY_TERM)
                authentication.create()
                self._entities.append(authentication)
                self._token_passwords.append(password)

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        return [0, 0, 3]

    def get_password(self, auth_index):
        """
        Returns the password for the authentication object

        :param auth_index: authentication object index
        :return: authentication object password
        :return: authentication object password
        """
        return self._token_passwords[auth_index]
