from base64 import b64encode, b64decode
from datetime import timedelta

from .entity import Entity
from .entity_exceptions import EntityNotFoundException
from .entity_sets.authentication_set import AuthenticationSet
from .entity_fields import RelatedEntityField, ManagedEntityField, \
    EntityPasswordManager, ExpiryDateManager
from .entity_providers.model_providers.authentication_provider import AuthenticationProvider


class Authentication(Entity):
    """
    Provides a single authentication object. Authentications are used to generate
    tokens and restore active session using tokens
    """

    AUTHENTICATION_TOKEN_SIZE = 20

    _entity_set_class = AuthenticationSet

    _entity_provider_list = [AuthenticationProvider()]

    _required_fields = ["user", "token_hash", "expiration_date"]

    _public_field_description = {
        "user": RelatedEntityField("core.entity.user.User",
                                   description="The user which this authentication belongs to"),
        "token_hash": ManagedEntityField(EntityPasswordManager,
                                         description="Token"),
        "expiration_date": ManagedEntityField(ExpiryDateManager,
                                              description="Token expiry date")
    }

    _current_user = None

    @classmethod
    def get_user(cls):
        """
        Defines the user that has been currently authenticated

        :return: 
        """
        return cls._current_user

    @classmethod
    def authenticate(cls, token):
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
        authentication_set = cls.get_entity_set_class()()
        authentication = authentication_set.get(int(token_id))
        if not authentication.token_hash.check(token_password):
            raise EntityNotFoundException()
        if authentication.expiration_date.is_expired():
            raise EntityNotFoundException()
        cls._current_user = authentication.user

    @classmethod
    def new_authentication(cls, user, expiry_term: timedelta) -> str:
        """
        Creates new authentication

        :param user: the user that wants to get a token
        :param expiry_term: the token expiration term
        :return: authentication token that shall be provided by the client application during each API request
        """
        authentication = cls(user=user)
        token_password = authentication.token_hash.generate(EntityPasswordManager.ALL_SYMBOLS,
                                                            size=cls.AUTHENTICATION_TOKEN_SIZE)
        authentication.expiration_date.set(expiry_term)
        authentication.create()
        token_id = authentication.id
        token = "%s:%s" % (token_id, token_password)
        return b64encode(token.encode("utf-8")).decode("utf-8")
