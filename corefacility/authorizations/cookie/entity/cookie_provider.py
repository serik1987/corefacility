from core.entity.entity_providers.model_providers.token_provider import TokenProvider

from ..models import Cookie as CookieModel


class CookieProvider(TokenProvider):
    """
    Exchanges the information between the cookie entity and the database.
    """

    _entity_class = "authorizations.cookie.entity.cookie.Cookie"
    _entity_model = CookieModel
