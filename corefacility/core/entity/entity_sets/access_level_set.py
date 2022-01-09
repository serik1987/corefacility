from core.models.enums import LevelType

from .entity_set import EntitySet
from ..entity_readers.access_level_reader import AccessLevelReader


class AccessLevelSet(EntitySet):
    """
    Allows to look for appropriate access level set
    """

    _entity_name = "Access level"

    _entity_class = "core.entity.access_level.AccessLevel"

    _entity_reader_class = AccessLevelReader

    _entity_filter_list = {
        "type": [lambda t: t, lambda t: t in (LevelType.project_level, LevelType.app_level)],
        "alias": [str, None],
    }
