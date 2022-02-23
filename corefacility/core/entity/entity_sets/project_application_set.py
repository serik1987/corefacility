from django.utils.translation import gettext_lazy as _

from .entity_set import EntitySet
from ..entity_readers.project_application_reader import ProjectApplicationReader


class ProjectApplicationSet(EntitySet):
    """
    Defines list of project applications attached to a certain entity.
    """

    _entity_name = _("Project application")

    _entity_class = "core.entity.project_application.ProjectApplication"
    """ Defines the entity class. Pass string value to this field to prevent circular import """

    _entity_reader_class = ProjectApplicationReader
    """
    Defines the entity reader class. The EntitySet interacts with external data source through the entity
    readers.
    """

    _entity_filter_list = {
        "application": ["core.entity.corefacility_module.CorefacilityModule", lambda module: module.is_application],
        "project": ["core.entity.project.Project", None],
        "is_enabled": [bool, None],
    }
