from .entity_set import EntitySet
from ..entity_readers.authentication_reader import AuthenticationReader


class AuthenticationSet(EntitySet):
    """
    An auxiliary class that is used to manage different authentications
    """

    _entity_name = "Authentication info"

    _entity_class = "core.entity.authentication.Authentication"

    _entity_reader_class = AuthenticationReader

    _entity_filter_list = {}
