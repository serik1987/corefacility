from core.models import ExternalAuthorizationSession as ExternalAuthorizationSessionModel

from .model_reader import ModelReader
from ..entity_providers.model_providers.external_authorization_session_provider \
    import ExternalAuthorizationSessionProvider


class ExternalAuthorizationSessionReader(ModelReader):
    """
    Retrieves the information about external authorization sessions from the database and saves it to the hard
    disk drive
    """

    _entity_model_class = ExternalAuthorizationSessionModel
    """ The entity model that is used for seeking a proper entity data """

    _entity_provider = ExternalAuthorizationSessionProvider()
