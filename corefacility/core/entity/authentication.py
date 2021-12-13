from .entity import Entity
from .entity_sets.authentication_set import AuthenticationSet
from .entity_fields import RelatedEntityField, ManagedEntityField, \
    EntityPasswordManager, ExpiryDateManager


class Authentication(Entity):
    """
    Provides a single authentication object. Authentications are used to generate
    tokens and restore active session using tokens
    """

    _entity_set_class = AuthenticationSet

    _entity_provider_list = []  # TO-DO: Write down all authentication providers here

    _required_fields = ["user", "token", "expiration_date"]

    _public_field_description = {
        "user": RelatedEntityField("core.entity.user.User",
                                   description="The user which this authentication belongs to"),
        "token_hash": ManagedEntityField(EntityPasswordManager,
                                         description="Token"),
        "expiration_date": ManagedEntityField(ExpiryDateManager,
                                              description="Token expiry date")
    }

    _user = None

    @classmethod
    def get_user(cls):
        """
        Defines the user that has been currently authenticated

        :return: 
        """
        return cls._user

    @classmethod
    def authenticate(cls, token):
        """
        Provides an authentication process using a given token

        :param token: the token that must be sent by the client application
        :return: the user authenticated
        """
        raise NotImplementedError("TO-DO: Authentication.authenticate")

    @classmethod
    def new_authentication(cls, user) -> str:
        """
        Creates new authentication

        :param user: the user that wants to get a token
        :return: authentication token that shall be provided by the client application during each API request
        """
        raise NotImplementedError("TO-DO: Authentication.new_authentication")
