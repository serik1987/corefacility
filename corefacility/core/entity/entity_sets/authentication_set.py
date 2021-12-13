from .entity_set import EntitySet


class AuthenticationSet(EntitySet):
    """
    An auxiliary class that is used to manage different authentications
    """

    _entity_name = "Authentication info"

    _entity_class = "core.entity.authentication.Authentication"

    _entity_reader_class = None  # TO-DO: Define proper authentication reader here!

    _entity_filter_list = {}
