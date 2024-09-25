from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType
from .cached_field import CachedField


class BasePathField(CachedField):
    """
    Defines the full canonical path for the base directory.
    """

    @property
    def _related_category(self):
        """
        Category that must be looked for the cache
        """
        if not self.entity.type == LabjournalRecordType.category:
            raise ValueError("The BasePathField is implemented for categories only")
        return self.entity

    def _get_value_from_cache_item(self, cache_item):
        """
        Extracts the value from the cache item

        :param cache_item: the cache item which value is needed to be extracted
        :return: the extracted value itself
        """
        return cache_item.base_directory
