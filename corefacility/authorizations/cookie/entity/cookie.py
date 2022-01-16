from core.entity.token import Token

from .cookie_set import CookieSet
from .cookie_provider import CookieProvider
from ..models import Cookie as CookieModel


class Cookie(Token):
    """
    Defines an authorization cookie as an entity
    """

    _entity_set_class = CookieSet

    _token_model = CookieModel

    _entity_provider_list = [CookieProvider()]
