from ..providers.model_providers.authentication_provider import AuthenticationProvider

from .token_reader import TokenReader


class AuthenticationReader(TokenReader):
    """
    Reads the authentications from the database
    """

    _entity_provider = AuthenticationProvider()

    _lookup_table_name = "core_application_authentication"

    _query_debug = False
