from .cached_field import CachedField


class DefaultValuesField(CachedField):
    """
    Represents default values of custom parameters.
    The default values are computed using the following rules.
    (1) If the parent category exists and the parameter value is defined here, default value of the record (even though
        this is category) equals to parameter value for its parent category.
    (2) If the parent category exists but the parameter value is not defined here, default value of the record
        equals to the default value of its parent category.
    (3) If the category is root, its default value equals to the default value of corresponding parameter descriptor.
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
        return cache_item.custom_parameters.copy()
