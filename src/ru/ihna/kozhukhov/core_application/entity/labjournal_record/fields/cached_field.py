from collections import deque

from ru.ihna.kozhukhov.core_application.entity.fields import ReadOnlyField
from ru.ihna.kozhukhov.core_application.utils import LabjournalCache


class CachedField(ReadOnlyField):
    """
    This is the base class for all fields with derivative values (i.e., those values that shall not be set by the user
    and should be calculated by the entity layer automatically).
    """

    entity = None
    """ The related entity """

    __record_set = None
    """ Working record set """

    _path_separator = '/'
    """ A symbol that separated category aliases inside the path """

    def proofread(self, value):
        """
        Proofreads the entity value. The method is called when the entity gets the field value to the user.
        Such value passes to the user itself who in turn proofreads such value

        :param value: the value stored in the entity as defined by one of the entity providers
        :return: the value given to the user
        """
        return self._get_value()

    @property
    def default(self):
        """
        Returns the default value of this entity field.
        The default value will be assigned to the entity if the entity is newly created rather than loaded from the
        external source and such value is not passed through the default constructor

        :return: the default value of this entity.
        """
        return self._get_value()

    @property
    def _record_set(self):
        """
        A record set that is used for looking for the parent category
        """
        if self.__record_set is None:
            from .. import RecordSet
            self.__record_set = RecordSet()
        return self.__record_set

    @property
    def _related_category(self):
        """
        Category that must be looked for the cache
        """
        raise NotImplementedError('related_category')

    def _get_value_from_cache_item(self, cache_item):
        """
        Extracts the value from the cache item

        :param cache_item: the cache item which value is needed to be extracted
        :return: the extracted value itself
        """
        raise NotImplementedError("_get_value_from_cache_item")

    def _get_value(self):
        """
        Returns the cached value.

        :return: the cached value to evaluate
        """
        if self.entity is None:
            raise ValueError("Please, specify the value of 'entity' public property")
        if self.entity.state == 'creating' or self.entity.state == 'deleted':
            return None  # We returned this value in order to print entities in 'creating' or 'deleted' state
        # Let's try to improve cache in such a way as loading the root record from cache is OK
        cache = LabjournalCache()
        related_category = self._related_category
        try:
            cache_item = cache.retrieve_category(related_category)
        except KeyError:
            cache_item = self._generate_cache_item(related_category)
            cache.put_category(cache_item)
        value = self._get_value_from_cache_item(cache_item)
        return value

    def _generate_cache_item(self, related_category):
        """
        Generates the cache item.

        :param related_category: a category which cache item should be generated
        :return: cache item to be generated
        """
        category_chain = deque()
        iteration_category = related_category
        while not iteration_category.is_root_record:
            if iteration_category.parent_category is None or iteration_category.alias is None or \
                    iteration_category.base_directory is None:
                iteration_category = self._record_set.get(iteration_category.id)
            category_chain.append(iteration_category)
            iteration_category = iteration_category.parent_category
        category_chain.reverse()

        if len(category_chain) > 0:
            category_path = self._path_separator + \
                            self._path_separator.join([category.alias for category in category_chain])
        else:
            category_path = "/"

        return LabjournalCache.create_cache_item(related_category, category_chain, category_path)
