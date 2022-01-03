from core.models import Project as ProjectModel
from .model_reader import ModelReader
from ..entity_providers.model_providers.project_provider import ProjectProvider


class ProjectReader(ModelReader):
    """
    Implements the project reader
    """

    _entity_provider = ProjectProvider()
    """
    The instance of the entity provider. When the EntityReader finds an information about
    the entity from the external source that satisfies filter conditions, it calls the
    wrap_entity method of the _entity_provider given here
    """

    _entity_model_class = ProjectModel
    """ The entity model that is used for seeking a proper entity data """
