from collections import namedtuple, OrderedDict
from django.conf import settings
from django.db import connection

from ..models import LabjournalCache as CacheDatabaseModel
from ..models.enums import LabjournalRecordType

LABJOURNAL_CACHE_MAX_SIZE = 1000


class LabjournalCache:
    """
    Caches results of calculations of values of derivative fields for the labjournal records.

    There are two caches. The cache 1 stores the data in the operating memory and resets everywhere when
    the Webserver or worker process restarts. The level 2 cache stores the data in the database and it doesn't restart.
    However, the cache 2 works more slowly than the level 1 cache.
    """

    CacheItem = namedtuple(
        "CategoryInfo",
        ['category', 'path', 'descriptors', 'custom_parameters', 'base_directory']
    )
    """ Auxiliary objects used for information transmission between the record entity and the cache """

    _instance = None
    """ The only instance of the class """

    _category_info_cache = None
    """ Cache for the category info """

    _category_path_cache = None
    """ Cache for category paths """

    def __new__(cls, *args, **kwargs):
        """
        Creates new cache instance if it doesn't exist. Retrieves the existent cache instance if it has already created.

        :param args: position arguments for the constructor
        :param kwargs: named arguments for the constructor
        """
        if cls._instance is None:
            cls._instance = super(LabjournalCache, cls).__new__(cls, *args, **kwargs)
            cls._instance.flush()
        return cls._instance

    def put_category(self, category_info: CacheItem):
        """
        Puts category information to cache.
        The method puts information both to the level 1 cache and the level 2 cache.

        :param category_info: information about the category to store into cache
        """
        self._put_category_to_cache_1(category_info)
        self._put_category_to_cache_2(category_info)

    def retrieve_category(self, category) -> CacheItem:
        """
        Takes category information from cache.
        The method looks for category information in the level 1 cache. If the information is absent in the level 1
        cache, it looks for information in the level 2 cache. If the information is absent in the level 2 cache
        the method throws KeyError.

        :param category: a category which information shall be taken from cache
        :return: the information about category stored inside the cache.
        """
        cache_item = self._retrieve_category_from_cache_1(category)
        if cache_item is None:
            cache_item = self._retrieve_category_from_cache_2(category)
            if cache_item is None:
                raise KeyError(category.id)
            else:
                self._put_category_to_cache_1(cache_item)
        return cache_item

    def retrieve_category_by_path(self, project, path: str) -> CacheItem:
        """
        Retrieves category that corresponds to related path from the cache.
        The method looks for category information in the level 1 cache. If the information is absent in the level 1
        cache, it looks for information in the level 2 cache. If the information is absent in the level 2 cache
        the method throws KeyError.

        :param project: the related project
        :param path: path to the category
        :return: the information about category stored inside the cache.
        """
        full_path = "%d:%s" % (project.id, path)
        cache_item = self._retrieve_category_by_path_from_cache_1(full_path)
        if cache_item is None:
            cache_item = self._retrieve_category_by_path_from_cache_2(full_path)
            if cache_item is None:
                raise KeyError(full_path)
            else:
                self._put_category_to_cache_1(cache_item)
        return cache_item

    def remove_category(self, category, old_alias):
        """
        Removes category as well as all children categories from the cache.
        The category will be removed both from the level 1 cache and the level 2 cache.

        :param category: a category to remove
        :param old_alias: old alias of the category
        """
        if category.parent_category.is_root_record:
            old_path = "%d:/%s" % (category.project.id, old_alias)
        else:
            from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RecordSet
            record_set = RecordSet()
            parent_category = record_set.get(category.parent_category.id)
            old_path = "%d:%s/%s" % (category.project.id, parent_category.path, old_alias)
        self._remove_category_from_cache_1(old_path)
        self._remove_category_from_cache_2(old_path)

    def flush(self):
        """
        Permanently removes all information about the level 1 and the level 2 categories from the cache.
        This function is used for simulation of Webserver restart during the cache tests execution.
        """
        if self._category_info_cache is not None:
            del self._category_info_cache
            del self._category_path_cache
        self._category_info_cache = OrderedDict()
        self._category_path_cache = dict()

    def _retrieve_category_from_cache_1(self, category):
        """
        Retrieves the category from the cache 1

        :param category: a category that shall be retrieved from the cache
        :return: a CacheItem containing information about that category or None if the category is not present
            in the cache 1
        """
        cache_item = None
        if category.id in self._category_info_cache:
            self._category_info_cache.move_to_end(category.id, last=True)
            cache_item = self._category_info_cache[category.id]
        return cache_item

    def _retrieve_category_by_path_from_cache_1(self, path):
        """
        Finds the category by path in the cache 1 and retrieve its related CacheItem

        :param path: the category path
        :return: a CacheItem containing information about that category or None if the category is not present
            in the cache 1
        """
        if path in self._category_path_cache:
            category_id = self._category_path_cache[path]
            cache_item = self._category_info_cache[category_id]
            self._category_info_cache.move_to_end(category_id, last=True)
        else:
            cache_item = None
        return cache_item

    def _put_category_to_cache_1(self, category_info):
        """
        Puts the category to the cache 1

        :param category_info: Information about the category that shall be put to the cache 1
        """
        self._category_info_cache[category_info.category.id] = category_info
        self._category_path_cache[category_info.path] = category_info.category.id
        if len(self._category_info_cache) > LABJOURNAL_CACHE_MAX_SIZE:
            _, extra_cache_item = self._category_info_cache.popitem(last=False)
            del self._category_path_cache[extra_cache_item.path]

    def _remove_category_from_cache_1(self, old_path):
        """
        Removes all information about the category as well as about all children categories from the cache

        :param old_path: path to the category since the last category save
        """
        cache_pairs_to_remove = [
            (path, category_id)
            for (path, category_id) in self._category_path_cache.items()
            if path.startswith(old_path)
        ]
        for category_path, category_id in cache_pairs_to_remove:
            del self._category_info_cache[category_id]
            del self._category_path_cache[category_path]

    def _retrieve_category_from_cache_2(self, category):
        """
        Retrieves the category from the cache 2

        :param category: a category that shall be retrieved from the cache
        :return: a CacheItem containing information about that category or None if the category is not present
            in the cache 2
        """
        try:
            cache_model = CacheDatabaseModel.objects.get(category_id=category.id)
            cache_item = self.CacheItem(
                category=category,
                path=cache_model.path,
                descriptors=cache_model.descriptors,
                custom_parameters=cache_model.custom_parameters,
                base_directory=cache_model.base_directory,
            )
        except CacheDatabaseModel.DoesNotExist:
            cache_item = None
        return cache_item

    def _retrieve_category_by_path_from_cache_2(self, path):
        """
        Retrieves the category from the cache 2 by its path

        :param path: a path to the category to be retrieved from the cache 1
        :return: a CacheItem containing information about that category or None if the category is not present
            in the cache 2
        """
        from ru.ihna.kozhukhov.core_application.entity.labjournal_record.record_provider import RecordProvider
        from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator
        from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.data_source import SqlTable
        from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters import StringQueryFilter
        cache_item_query_builder = settings.QUERY_BUILDER_CLASS() \
            .add_select_expression('cache.category_id') \
            .add_select_expression('cache.path') \
            .add_select_expression('cache.descriptors') \
            .add_select_expression('cache.custom_parameters') \
            .add_select_expression('cache.base_directory') \
            .add_select_expression('record.parent_category_id') \
            .add_select_expression('record.project_id') \
            .add_data_source(SqlTable('core_application_labjournalcache', 'cache')) \
            .set_main_filter(StringQueryFilter('cache.path=%s', path))
        cache_item_query_builder.data_source.add_join(
            cache_item_query_builder.JoinType.INNER,
            SqlTable("core_application_labjournalrecord", 'record'),
            "ON (record.id = cache.category_id)"
        )
        with connection.cursor() as cursor:
            cache_item_query = cache_item_query_builder.build()
            cursor.execute(cache_item_query[0], cache_item_query[1:])
            fetch_result = cursor.fetchone()
        if fetch_result is not None:
            category_id, path, descriptors, custom_parameters, base_directory, parent_category_id, project_id \
                = fetch_result
            record_provider = RecordProvider()
            record_provider.current_type = LabjournalRecordType.category
            cache_item = self.CacheItem(
                category=record_provider.wrap_entity(ModelEmulator(
                    id=category_id,
                    project=ModelEmulator(
                        id=project_id,
                        root_group=None,
                    ),
                    parent_category_id=parent_category_id,
                    parent_category=ModelEmulator(
                        id=parent_category_id,
                    ),
                )),
                path=path,
                descriptors=descriptors,
                custom_parameters=custom_parameters,
                base_directory=base_directory,
            )
        else:
            cache_item = None
        return cache_item

    def _put_category_to_cache_2(self, category_info):
        """
        Puts the category to the cache 2

        :param category_info: information about the category to put to the cache 2
        """
        CacheDatabaseModel(
            category_id=category_info.category.id,
            path=category_info.path,
            descriptors=category_info.descriptors,
            custom_parameters=category_info.custom_parameters,
            base_directory=category_info.base_directory,
        ).save()

    def _remove_category_from_cache_2(self, old_path):
        """
        Removes the category together with all its paths from the cache 2

        :param old_path: path to the category since the last category save
        """
        CacheDatabaseModel.objects \
            .filter(path__startswith=old_path) \
            .delete()
