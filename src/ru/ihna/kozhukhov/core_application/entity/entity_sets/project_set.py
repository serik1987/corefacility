from django.utils.translation import gettext_lazy as _
from .entity_set import EntitySet
from ..readers.project_reader import ProjectReader


class ProjectSet(EntitySet):
    """
    Implements the project searching facilities
    """

    _entity_name = _("Project")

    _entity_class = "core.entity.project.Project"

    _entity_reader_class = ProjectReader

    _entity_filter_list = {
        "name": [str, None],
        "user": [
            "ru.ihna.kozhukhov.core_application.entity.user.User",
            lambda user: user.state not in {"creating", "deleted"}
        ],
        "root_group": [
            "ru.ihna.kozhukhov.core_application.entity.group.Group",
            lambda group: group.state not in {"creating", "deleted"}
        ],
        "application": [
            "ru.ihna.kozhukhov.core_application.entity.corefacility_module.CorefacilityModule",
            lambda module: module.is_application
        ],
    }
