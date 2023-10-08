from .entity_set import EntitySet
from ru.ihna.kozhukhov.core_application.entity.readers.authentication_reader import AuthenticationReader


class AuthenticationSet(EntitySet):
    """
    An auxiliary class that is used to manage different authentications.
    """

    _entity_name = "Authentication info"

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.authentication.Authentication"

    _entity_reader_class = AuthenticationReader

    _entity_filter_list = {}
