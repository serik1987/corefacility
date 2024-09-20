from collections import OrderedDict

from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType
from .cached_field import CachedField


class ComputedDescriptorsField(CachedField):
    """
    A field that evaluates descriptors for custom parameters that can be adjusted for this particular record
    """

    @property
    def _related_category(self):
        """
        Category that must be looked for the cache
        """
        if self.entity.type == LabjournalRecordType.category:
            related_category = self.entity
        else:
            related_category = self.entity.parent_category
        return related_category

    def _get_value_from_cache_item(self, cache_item):
        """
        Extracts the value from the cache item

        :param cache_item: the cache item which value is needed to be extracted
        :return: the extracted value itself
        """
        if cache_item.descriptors is None or len(cache_item.descriptors) == 0:
            descriptors = OrderedDict()
        else:
            descriptors = cache_item.descriptors.copy()
        return descriptors
