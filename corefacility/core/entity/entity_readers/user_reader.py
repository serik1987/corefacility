from core.models import User

from .model_reader import ModelReader
from ..entity_providers.model_providers.user_provider import UserProvider


class UserReader(ModelReader):
    """
    Allows to retrieve users from the database
    """

    _entity_model_class = User
    """ The entity model that is used for seeking a proper entity data """

    _entity_provider = UserProvider()
    """
    The instance of the entity provider. When the EntityReader finds an information about
    the entity from the external source that satisfies filter conditions, it calls the
    wrap_entity method of the _entity_provider given here
    """
