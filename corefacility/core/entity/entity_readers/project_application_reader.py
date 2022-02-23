from core.models import ProjectApplication as ProjectApplicationModel

from .model_reader import ModelReader
from ..entity_providers.model_providers.project_application_provider import ProjectApplicationProvider


class ProjectApplicationReader(ModelReader):
    """
    Seeks for information about certain ProjectApplication entity in the database and passes its information
    to the ProjectApplicationProvider
    """

    _entity_model_class = ProjectApplicationModel
    """ The entity model that is used for seeking a proper entity data """

    _entity_provider = ProjectApplicationProvider()
