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
        if self.entity.is_root_record:
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
        if self.entity.is_root_record:
            path = "/"
        elif self.entity.parent_category.is_root_record:
            path = "/%s" % self.entity.alias
        else:
            _, related_category_path = cache_item.path.split(":")
            path = "%s/%s" % (related_category_path, self.entity.alias)
        return path
