from django.utils.translation import gettext_lazy as _
from .entity_set import EntitySet
from ..entity_readers.project_reader import ProjectReader


class ProjectSet(EntitySet):
    """
    Implements the project searching facilities
    """

    _entity_name = _("Project")

    _entity_class = "core.entity.project.Project"

    _entity_reader_class = ProjectReader

    _entity_filter_list = {
        "name": [str, None],
        "user": ["core.entity.user.User", lambda user: user.state not in {"creating", "deleted"}],
        "application": ["core.entity.corefacility_module.CorefacilityModule", lambda module: module.is_application]
    }
