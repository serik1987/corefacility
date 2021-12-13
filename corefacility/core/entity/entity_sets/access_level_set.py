from core.models.enums import LevelType
from .entity_set import EntitySet


class AccessLevelSet(EntitySet):
    """
    Allows to look for appropriate access level set
    """

    _entity_name = "Access level"

    _entity_class = "core.entity.access_level.AccessLevel"

    _entity_reader_class = None   # TO-DO: define a proper access level reader

    _entity_filter_list = {
        "type": [lambda t: t, lambda t: t in (LevelType.project_level, LevelType.app_level)],
        "alias": [str, None],
    }
