from datetime import timedelta

from .entity_object import EntityObject


class TokenObject(EntityObject):
    """
    An abstract base class for CookieObject and AuthenticationObject
    """

    TOTAL_SYMBOL_NUMBER = 20
    EXPIRATION_TERM = timedelta(seconds=1)

    _initial_password = None

    def __init__(self, use_defaults=True, **kwargs):
        """
        Creates the entity object that results to creating an entity

        :param use_defaults: if True, the constructor will use the _default_create_kwargs fields. Otherwise, this
        class property will be ignored
        :param kwargs: Any additional field values that shall be embedded to the entity or 'id' that reflects the
        entity ID
        """
        super().__init__(use_defaults, **kwargs)

        self._initial_password = self.entity.token_hash.generate(self.entity.token_hash.ALL_SYMBOLS,
                                                                 self.TOTAL_SYMBOL_NUMBER)
        self._entity_fields['token_hash'] = "*****"

        self.entity.expiration_date.set(self.EXPIRATION_TERM)
        self._entity_fields['expiration_date'] = self.EXPIRATION_TERM

    @property
    def initial_password(self):
        """
        The password given to the token when this is still created
        """
        return self._initial_password

    @property
    def default_field_key(self):
        """
        Defines names of all default keyword arguments

        :return: list of all keys
        """
        return {"user", "token_hash", "expiration_date"}
