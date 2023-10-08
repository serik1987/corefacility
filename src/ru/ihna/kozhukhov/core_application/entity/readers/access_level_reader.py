import ru.ihna.kozhukhov.core_application.models as models

from .model_reader import ModelReader
from ..providers.model_providers.access_level_provider import AccessLevelProvider


class AccessLevelReader(ModelReader):
    """
    Organizes loading access levels from the database and provides interface negotiation between
    entity layer and the Django model layer
    """

    _entity_model_class = models.AccessLevel
    """ The entity model that is used for seeking a proper entity data """

    _entity_provider = AccessLevelProvider()
    """ The entity provider will transform access level Django models to access level entities """
