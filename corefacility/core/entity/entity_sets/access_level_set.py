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
        "type": [LevelType, None],
    }

    @staticmethod
    def project_level(alias: str):
        """
        Retrieves the project access level from the database.

        :param alias: access level alias
        :return: the AccessLevel object
        """
        access_level_set = AccessLevelSet()
        access_level_set.type = LevelType.project_level
        return access_level_set.get(alias)

    @staticmethod
    def application_level(alias: str):
        """
        Retrieves the application access level from the database.

        :param alias: access level alias
        :return: the AccessLevel object
        """
        access_level_set = AccessLevelSet()
        access_level_set.type = LevelType.app_level
        return access_level_set.get(alias)
