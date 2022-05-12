from base64 import b64encode, b64decode
from datetime import datetime, timedelta
from django.utils import timezone

from .entity import Entity
from .entity_exceptions import EntityNotFoundException
from .entity_fields import RelatedEntityField, ManagedEntityField, EntityPasswordManager, ExpiryDateManager


class Token(Entity):
    """
    This is the base class for all internally issuing tokens including cookie and authentication tokens.

    Any token contains two fields separated by the colon symbol (':'): the token ID and the token password.
    The token ID is needed to easily find the token in the database while token password is used to check
    whether valid token is given
    """

    TOKEN_PASSWORD_SIZE = 20
    """ Maximum size of the token password """

    _required_fields = ["user", "token_hash", "expiration_date"]

    __initial_field_description = {
        "user": RelatedEntityField("core.entity.user.User",
                                   description="The user which this authentication belongs to"),
        "token_hash": ManagedEntityField(EntityPasswordManager, description="Token"),
        "expiration_date": ManagedEntityField(ExpiryDateManager, description="Token expiry date")
    }

    _additional_field_description = {}
    """
    If some additional fields are needed for the token put them here.
    The dictionary is like _public_field_description
    """

    _current_user = None

    def __init__(self, **kwargs):
        """
        Initializes the token

        :param kwargs: values of public or protected fields you need to be initially set
        """
        self._public_field_description = self.__initial_field_description.copy()
        self._public_field_description.update(self._additional_field_description)
        super().__init__(**kwargs)

    @classmethod
    def get_user(cls):
        """
        Defines the user that has been currently authenticated

        :return:
        """
        return cls._current_user

    @classmethod
    def apply(cls, token):
        """
        Provides an authentication process using a given token

        :param token: the token that must be sent by the client application
        :return: the user authenticated
        """
        try:
            token_info = b64decode(token.encode("utf-8")).decode("utf-8")
            token_id, token_password = token_info.split(":", maxsplit=1)
        except ValueError:
            raise EntityNotFoundException()
        token_set = cls.get_entity_set_class()()
        token_entity = token_set.get(int(token_id))
        if token_entity.expiration_date.is_expired():
            raise EntityNotFoundException()
        if not token_entity.token_hash.check(token_password):
            raise EntityNotFoundException()
        cls._current_user = token_entity.user
        return token_entity

    @classmethod
    def issue(cls, user, expiry_term: timedelta) -> str:
        """
        Creates new authentication

        :param user: the user that wants to get a token
        :param expiry_term: the token expiration term
        :return: authentication token that shall be provided by the client application during each API request
        """
        token_entity = cls(user=user)
        token_password = token_entity.token_hash.generate(EntityPasswordManager.ALL_SYMBOLS,
                                                          size=cls.TOKEN_PASSWORD_SIZE)
        token_entity.expiration_date.set(expiry_term)
        token_entity.create()
        token_id = token_entity.id
        token = "%s:%s" % (token_id, token_password)
        return b64encode(token.encode("utf-8")).decode("utf-8")

    @classmethod
    def clear_all_expired_tokens(cls):
        t = timezone.make_aware(datetime.now())
        cls._token_model.objects.filter(expiration_date__lt=t).delete()

    def refresh(self, expiry_term):
        """
        Refreshes the token

        :param expiry_term: token expiry term
        :return: nothing
        """
        self.expiration_date.set(expiry_term)
        self.update()

    def __eq__(self, other):
        """
        Compares two tokens

        :param other: another token to which this token shall be compared
        :return: True if two tokens are the same, False otherwise.
        """
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False
