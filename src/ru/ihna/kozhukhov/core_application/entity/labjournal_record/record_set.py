import re
from collections import deque
from enum import Enum

from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.entity.entity_sets.entity_set import EntitySet
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.models import LabjournalRootRecord, LabjournalRecord
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator
from .complex_interval import ComplexInterval
from .record_reader import RecordReader
from .root_record_provider import RootRecordProvider
from ..project import Project
from ...exceptions.entity_exceptions import EntityNotFoundException
from ...utils import LabjournalCache


class RecordSet(EntitySet):
    """
    Manipulates the list of labjournal records stored in the database

    Available filters:
    parent_category show children belonging to a particular parent_category (not suitable for the root record)
    user Defines the user context for the record (not suitable for the root record)
    alias The record alias (not suitable for the root record)
    type The record type filter (not suitable for the root record)
    """

    class LogicType(Enum):
        """
        Represents one of the predefined logic types
        """
        AND = "and"
        OR = "or"

    root_child_path = re.compile(r'^/([A-Za-z0-9\-_]+)$')
    general_path = re.compile(r'^(/[A-Za-z0-9\-_/]+)/([A-Za-z0-9\-_]+)$')
    general_path_parent_category_position = 1
    general_path_alias_position = 2

    _entity_name = _("Laboratory journal record")
    """ Default human-readable name of the entity """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_record.record.Record"
    """ Base class of all entities containing inside this particular RecordSet """

    _entity_reader_class = RecordReader
    """ Entity readers are responsible for picking entities from the database """

    _root_record_provider = RootRecordProvider()
    """ Deals especially with root record """

    _entity_filter_list = {
        'parent_category':
            ("ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record.CategoryRecord", None),
        'user': ("ru.ihna.kozhukhov.core_application.entity.user.User", None),
        'alias': (str, None),
        'type': (LabjournalRecordType, None),
        'datetime': (ComplexInterval, None),
        'types': (list, None),
        'name': (str, None),
        'hashtags': (list, None),
        'hashtag_logic': (LogicType, None),
    }
    """ List of all entity filters """

    _alias_kwarg = None
    """
    The entity retrieval is available either by its numerical ID or by its full path which is not a database field
    """

    def get_root(self, project):
        """
        Reads the root record (the ordinary methods such as indexation, slicing, get(), len etc. usually doesn't
        read the parent categories)
        """
        try:
            external_object = LabjournalRootRecord.objects.get(project_id=project.id)
        except LabjournalRootRecord.DoesNotExist:
            external_object = ModelEmulator(
                comments=None,
                base_directory=None,
                project=project,
            )
        record = self._root_record_provider.wrap_entity(external_object)
        return record

    def get(self, lookup):
        """
        Finds the record by its ID or by a pair (project, path)
        Record ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity path is a short string that exists in the HTTP request path and helps to route a given record.
        The root record always has the path equal to '/'. The path of a child of the root record is its alias
        attached to the "/" string. The path any other record is path of its parent record plus "/" sign plus
        alias of the record. As you can see, the category can be unambiguously defined by its path inside the
        laboratory journal. However, there can be two records with the same path that can be related to two different
        laboratory journals. Hence, to unambiguously identify the record by its path you have to point out a project
        which laboratory journal you consider together with the record path. You need to use (project, path) as a value
        of the lookup argument in this case.

        The function must be executed in one request.

        During the execution of this method parent_category and alias filters will be temporary disabled.

        :param lookup: record ID or (project, path) pair
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        if isinstance(lookup, str) and self.parent_category is  None:
            raise ValueError("The record can't be unambiguously defined by its alias and/or its path")
        elif isinstance(lookup, tuple) and len(lookup) == 2:
            project, path = lookup
            if not isinstance(project, Project) or not isinstance(path, str):
                raise ValueError("The record can be identified either by its ID or by its (project, lookup) pair")
            root_child_match = self.root_child_path.match(path)
            general_path_match = self.general_path.match(path)
            if path == "/":
                parent_category_path = "/"
                alias = None
            elif root_child_match is not None:
                parent_category_path = "/"
                alias = root_child_match[1]
            elif general_path_match is not None:
                parent_category_path = general_path_match[self.general_path_parent_category_position]
                alias = general_path_match[self.general_path_alias_position]
            else:
                raise EntityNotFoundException()
            cache = LabjournalCache()
            try:
                cache_item = cache.retrieve_category_by_path(project, parent_category_path)
            except KeyError:
                cache_item = self._evaluate_category_by_path(project, parent_category_path)
                cache.put_category(cache_item)
            if path == "/":
                record = self.get_root(project)
            else:
                record = self.get_by_parent_category_and_alias(cache_item.category, alias)
            return record
            # if path == "/":
            #     return self.get_root(project)
            # root_child_match = self.root_child_path.match(path)
            # general_path_match = self.general_path.match(path)
            # if root_child_match is not None:
            #     from .root_category_record import RootCategoryRecord
            #     parent_category = RootCategoryRecord(project=project)
            #     alias = root_child_match[1]
            # elif general_path_match is not None:
            #     parent_category_path = general_path_match[self.general_path_parent_category_position]
            #     alias = general_path_match[self.general_path_alias_position]
            #     cache = LabjournalCache()
            #     try:
            #         cache_item = cache.retrieve_category_by_path(project, parent_category_path)
            #     except KeyError:
            #         cache_item = self._evaluate_category_by_path(project, parent_category_path)
            #         cache.put_category(cache_item)
            #     parent_category = cache_item.category
            # else:
            #     raise EntityNotFoundException()
            # return self.get_by_parent_category_and_alias(parent_category, alias)
        else:
            return super().get(lookup)

    def get_by_parent_category_and_alias(self, parent_category, alias):
        """
        Reveals the record by its parent category and alias.

        The function must be executed in one request.

        During the execution of this method parent_category and alias filters will be temporary disabled.

        :param parent_category: the parent category for the cue
        :param alias: the category alias
        """
        reader = self.entity_reader_class(
            **self._entity_filters,
            parent_category=parent_category,
            alias=alias,
        )
        provider = reader.get_entity_provider()
        external_object = reader.get()
        return provider.wrap_entity(external_object)

    def _evaluate_category_by_path(self, project, parent_category_path):
        """
        Evaluates the category by its path

        :param project: related project
        :param parent_category_path: path for the parent category
        :return: the CacheItem related to the category
        """
        from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RootCategoryRecord
        if parent_category_path == "/":
            path_terms = ['']
        else:
            path_terms = parent_category_path.split("/")
        category = RootCategoryRecord(project=project)
        reader = self.entity_reader_class()
        provider = reader.get_entity_provider()
        provider.current_type = LabjournalRecordType.category
        category_chain = deque()
        for path_term in path_terms[1:]:
            try:
                category_model = LabjournalRecord.objects.get(
                    project_id=project.id,
                    parent_category_id=category.id,
                    alias=path_term,
                )
                category = provider.wrap_entity(ModelEmulator(
                    id=category_model.id,
                    alias=path_term,
                    parent_category_id=category.id,
                    parent_category=category,
                    project=project,
                ))
                category_chain.append(category)
            except LabjournalRecord.DoesNotExist:
                raise EntityNotFoundException()
        return LabjournalCache.create_cache_item(category, category_chain, parent_category_path)
        # cache_item = LabjournalCache.CacheItem(
        #     category=category,
        #     path="%d:%s" % (category.project.id, parent_category_path),
        #     descriptors=None,
        #     custom_parameters=None,
        #     base_directory=None,
        # )
        # return cache_item