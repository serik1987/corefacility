from ....entity.readers.token_reader import TokenReader

from .cookie_provider import CookieProvider


class CookieReader(TokenReader):
    """
    Builds token searching queries and send them to the database.
    """

    _entity_provider = CookieProvider()

    _lookup_table_name = "auth_cookie_cookie"

    _query_debug = False
