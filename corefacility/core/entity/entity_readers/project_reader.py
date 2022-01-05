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

    _filter_map = {
        "name": "name__istartswith",
    }
    """
    Establishes the correspondence between EntitySet filter name and Django model manager filter name
    All EntitySet filters that were present in this maps will be substituted to the Django model manager filter
    names related to corresponding values.
    If the EntitySet filter is absent here this mean that both filter names were the same.
    """
