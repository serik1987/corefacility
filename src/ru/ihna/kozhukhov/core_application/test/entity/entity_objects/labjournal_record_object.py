from datetime import datetime, timedelta

from ru.ihna.kozhukhov.core_application.entity.entity_sets.project_set import ProjectSet
from ru.ihna.kozhukhov.core_application.entity.entity_sets.user_set import UserSet
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record import CategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.data_record import DataRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.service_record import ServiceRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.record_set import RecordSet
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType

from .entity_object import EntityObject

RECORD_TYPES = {
    'category': CategoryRecord,
    'data': DataRecord,
    'service': ServiceRecord,
}

RECORD_TYPE_VALUES = {
    'category': LabjournalRecordType.category,
    'data': LabjournalRecordType.data,
    'service': LabjournalRecordType.service,
}

RELATIVE_TIMES = {
    'hour': timedelta(hours=1, minutes=10),
    'day': timedelta(days=1, hours=10),
    'year': timedelta(days=366),
    'inf': timedelta(days=3600),
}


class LabjournalRecordObject(EntityObject):
    """
    Allows to modify the labjournal record from the side of the test_labjournal_record
    """

    _default_create_kwargs = {
        "parent_category": "root",
        "level": 1,
        "project": "the_rabbit_project",
        "alias": "A",
        "user": "leader",
        "checked": False,
        "type": "category",
        "comments": "Прочая информация об указанной записи",
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        "alias": "B",
        "user": "no_leader",
        "checked": True,
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """

    _entity_kwargs = None
    """ The kwargs that was used during the last creation of the entity """

    projects = dict()
    """ Represents all projects """

    user_contexts = {
        'optical_imaging': {
            'leader': 'user2',
            'no_leader': 'user1',
        },
        'the_rabbit_project': {
            'leader': 'user4',
            'no_leader': 'user6'
        }
    }
    """ Represents leaders of all projects """

    @property
    def entity_fields(self):
        """
        The entity fields. When some values were assigned to the entity fields their copy will be assigned here.
        Next, when the entity is loaded these fields will be checked
        """
        fields = super().entity_fields.copy()
        del fields['type']
        return fields

    def get_new_entity(self, options):
        """
        Creates the new Entity object and fills its fields by the options dictionary

        :param options: the field => value dictionary to prefill the entity fields
        :return: the entity created
        """
        if options['parent_category'] is not None:
            record_class = RECORD_TYPES[options['type']]
            parent_category = self.get_parent_category(options['parent_category'], options['project'], options['level'])
            category_start_date = parent_category.datetime
            if category_start_date is None:
                category_start_date = datetime(2024, 1, 1, 0, 0)
            user_context = self.get_user_context(parent_category.project, options['user'])
            record = record_class(
                parent_category=parent_category,
                user=user_context,
                checked=options['checked'],
                comments=options['comments'],
            )
            if not isinstance(record, ServiceRecord):
                record.alias = options['alias']
            if not isinstance(record, CategoryRecord):
                record.datetime = category_start_date+RELATIVE_TIMES[options['relative_time']]
            self._entity_kwargs = options
        else:
            project = self.get_project(options['project'])
            record = RootCategoryRecord(
                project=project,
                user=self.get_user_context(project, options['user']),
            )
        return record

    def set_field(self, name, value, options):
        """
        Modifies the entity fields

        :param name: name of the field to modify
        :param value: the modifying value
        :param options: all other options
        """
        if name == "parent_category" or name == 'project' or name == 'level':
            if 'parent_category' not in options or 'project' not in options or 'level' not in options:
                raise ValueError("Can't change any of these fields separately: parent_category, project, level")
            self._entity.parent_category \
                = self.get_parent_category(options['parent_category'], options['project'], options['level'])
        elif name == "user":
            self._entity.user = self.get_user_context(self._entity.project, value)
        else:
            setattr(self._entity, name, value)

    @property
    def default_field_key(self):
        """
        Returns keys from all default keyword args, just for additional checks

        :return:
        """
        field_keys = set(self._default_create_kwargs.keys())
        field_keys.remove('type')
        return field_keys

    def get_project(self, alias):
        """
        Gets the project by alias

        :param alias: the alias to lookup
        :return: the project itself
        """
        if alias not in self.projects:
            self.projects[alias] = ProjectSet().get(alias)
        return self.projects[alias]

    def get_parent_category(self, parent_category, project_alias, level):
        """
        Finds the parent category for a given project

        :param parent_category: a short string that cues what kind of parent category we need
            'root' the root category
            'no_root' any category inside the root category
        :param project_alias: alias of the project inside which the parent category is located
        :param level: the desired level of parent category (applicable when the parent_category is 'no_root')
        :return: the parent category (a CategoryRecord instance)
        """
        project = self.get_project(project_alias)
        if parent_category == 'root':
            current_level = 0
        elif parent_category == 'no_root':
            current_level = level-1
        else:
            raise NotImplementedError("Unrecognized cue for the parent category: %s" % parent_category)
        category = RootCategoryRecord(project=project)
        record_set = RecordSet()
        while current_level > 0:
            current_level -= 1
            record_set.parent_category = category
            record_set.type = LabjournalRecordType.category
            category = record_set[0]
        return category

    def get_user_context(self, project, status):
        """
        Returns the user context for a given project

        :param project: the project inside which the record is created
        :param status: 'leader' to look for the project leader, 'no_leader' to don't look at the project leader
        """
        if isinstance(self.user_contexts[project.alias][status], str):
            self.user_contexts[project.alias][status] = UserSet().get(self.user_contexts[project.alias][status])
        return self.user_contexts[project.alias][status]

    def reload_entity(self):
        """
        Loads the recently saved entity from the database

        :return: nothing
        """
        entity_set = self._entity.get_entity_set_class()()
        if self.entity_fields['parent_category'] is None:
            entity_set.parent_category = None
            self._entity = entity_set.get_root(self._entity.project)
        else:
            if self._id is None:
                raise RuntimeError("LabjournalRecordObject.reload_entity: can't reload the entity that was not created")
            entity_set.user = self._entity.user
            self._entity = entity_set.get(self._id)
