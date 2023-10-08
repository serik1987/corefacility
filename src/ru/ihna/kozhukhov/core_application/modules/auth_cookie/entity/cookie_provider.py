from ....entity.providers.model_providers.token_provider import TokenProvider

from ..models import Cookie as CookieModel


class CookieProvider(TokenProvider):
    """
    Exchanges the information between the cookie entity and the database.
    """

    _entity_class = "ru.ihna.kozhukhov.core_application.modules.auth_cookie.entity.cookie.Cookie"
    _entity_model = CookieModel
