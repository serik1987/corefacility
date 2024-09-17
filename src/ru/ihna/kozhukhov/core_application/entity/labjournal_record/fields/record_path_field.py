from .cached_field import CachedField


class RecordPathField(CachedField):
    """
    Represents the record path, if necessary
    """

    @property
    def _related_category(self):
        """
        Category that must be looked for the cache
        """
        return self.entity.parent_category

    def _get_value_from_cache_item(self, cache_item):
        """
        Extracts the value from the cache item

        :param cache_item: the cache item which value is needed to be extracted
        :return: the extracted value itself
        """
        _, related_category_path = cache_item.path.split(":")
        return "%s/%s" % (related_category_path, self.entity.alias)
