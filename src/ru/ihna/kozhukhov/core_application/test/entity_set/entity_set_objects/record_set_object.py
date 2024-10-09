from datetime import datetime, timedelta

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RecordSet
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record import CategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.data_record import DataRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.record import Record
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.service_record import ServiceRecord
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityNotFoundException
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from .entity_set_object import EntitySetObject


class RecordSetObject(EntitySetObject):
    """
    Represents the manipulator of the record set for testing purposes.
    """

    optical_imaging = None
    the_rabbit_project = None
    leaders = None
    no_leaders = None

    _project_set_object = None

    _entity_class = Record

    def __init__(self, user_set_object, project_set_object, _entity_list=None):
        """
        Initializes new record set

        :param user_set_object: users that will be used to form records in the laboratory journal
        :param project_set_object: projects that will be used to form records in the laboratory journal
        :param _entity_list: for service purpose only
        """
        self._user_set_object = user_set_object
        self._project_set_object = project_set_object

        try:
            self.optical_imaging = self._project_set_object.get_by_alias('hhna')
            self.optical_imaging.alias = 'optical_imaging'
            self.optical_imaging.name = "Оптическое картирование по внутреннему сигналу"
            self.optical_imaging.update()
        except EntityNotFoundException:
            self.optical_imaging = self._project_set_object.get_by_alias('optical_imaging')

        try:
            self.the_rabbit_project = self._project_set_object.get_by_alias('mnl')
            self.the_rabbit_project.alias = 'the_rabbit_project'
            self.the_rabbit_project.name = "Миндалина кролика"
            self.the_rabbit_project.update()
        except EntityNotFoundException:
            self.the_rabbit_project = self._project_set_object.get_by_alias('the_rabbit_project')

        self.leaders = {
            'optical_imaging': self._user_set_object.get_by_alias('user2'),
            'the_rabbit_project': self._user_set_object.get_by_alias('user4'),
        }

        self.no_leaders = {
            'optical_imaging': self._user_set_object.get_by_alias('user1'),
            'the_rabbit_project': self._user_set_object.get_by_alias('user6'),
        }

        if _entity_list is not None:
            super().__init__(_entity_list=_entity_list)
        else:
            self._entities = list()
            for project in self.optical_imaging, self.the_rabbit_project:
                root_record = RootCategoryRecord(project=project)
                current_date = datetime(2024, 1, 1, 0, 0)
                finish_date = datetime(2024, 2, 1, 0, 0)
                alias = 'a'
                index = 1
                while current_date <= finish_date:
                    parent_category = CategoryRecord(
                        parent_category=root_record,
                        alias=alias,
                        user=self.leaders[project.alias],
                        checked=index % 2 == 0,
                        comments="Родительская категория",
                    )
                    parent_category.create()
                    current_time = current_date
                    subindex = 1
                    while current_time <= current_date + timedelta(days=1):
                        record = DataRecord(
                            parent_category=parent_category,
                            alias=alias + str(subindex),
                            datetime=current_time,
                            user=self.leaders[project.alias],
                            checked=subindex % 2 == 1,
                            comments="Запись экспериментальных данных"
                        )
                        record.create()
                        self._entities.append(record)
                        current_time += timedelta(hours=4)
                        subindex += 1
                    current_time = current_date
                    subindex = 1
                    while current_time <= current_date + timedelta(days=1):
                        record = ServiceRecord(
                            parent_category=parent_category,
                            name="Служебная запись " + str(subindex),
                            datetime=current_time,
                            user=self.leaders[project.alias],
                            checked=subindex % 3 == 0,
                            comments="Служебная запись"
                        )
                        record.create()
                        self._entities.append(record)
                        subindex += 1
                        current_time += timedelta(hours=6)
                    record = CategoryRecord(
                        parent_category=parent_category,
                        alias="subcat",
                        comments="Категория"
                    )
                    record.create()
                    self._entities.append(record)
                    parent_category = RecordSet().get(parent_category.id)
                    self._entities.append(parent_category)
                    current_date += timedelta(days=1)
                    alias = alias[:-1] + chr(ord(alias[-1]) + 1)
                    if alias[-1] == "{":
                        alias = alias[:-1] + "aa"
                    index += 1

    def sort(self):
        """
        Sorts all entities inside the entity container in the default order.
        Remains all entities in the database unchanged.
        """
        self._entities = sorted(self._entities,
                                key=lambda record: record.datetime
                                if record.datetime is not None
                                else datetime(1900, 1, 1))  # NULLS first!

    def clone(self):
        """
        Returns an exact copy of the container
        """
        return self.__class__(self._user_set_object, self._project_set_object, _entity_list=list(self._entities))

    def filter_by_parent_category(self, parent_category):
        """
        Applies the parent category filter.
        Remains all entities in the database unchanged.

        :param parent_category: remains only records with given parent category
        """
        self._entities = list(filter(lambda record: record.parent_category.id == parent_category.id, self._entities))

    def filter_by_datetime(self, complex_interval):
        """
        Applies filtration by the datetime.
        Remains all entities in the database unchanged.

        :param complex_interval: an instance of the ComplexInterval value that denotes what to use
        """
        self._entities = list(filter(
            lambda record: record.datetime is not None and record.datetime in complex_interval, self._entities
        ))

    def filter_by_types(self, types):
        """
        Apply filtration by possible types.
        Remains all entities in the database unchanged.

        :param types: an iterable object containing all valid types
        """
        self._entities = list(filter(lambda record: record.type in types, self._entities))

    def filter_by_name(self, name):
        """
        Filter only those records which name starts from a given line.
        Remains all entities in the database unchanged.

        :param name: the record name
        """
        self._entities = list(filter(
            lambda record: record.type == LabjournalRecordType.service and record.name.startswith(name), self._entities
        ))

    def filter_by_custom_parameters(self, custom_parameters):
        """
        Remains only such entities inside the entity container that have certain custom parameters.
        Remains all entities in the database unchanged.

        :param custom_parameters: a dictionary for all available custom parameters plus '_logic' hidden parameter for
        representing the logic
        """
        if custom_parameters['_logic'] == RecordSet.LogicType.AND:
            def filter_function(record):
                record_shall_be_remained = True
                for name, value in custom_parameters.items():
                    if name[0] == '_':
                        continue
                    param_name = 'custom_%s' % name
                    if getattr(record, param_name) != value:
                        record_shall_be_remained = False
                        break
                return record_shall_be_remained
        elif custom_parameters['_logic'] == RecordSet.LogicType.OR:
            def filter_function(record):
                record_shall_be_remained = False
                for name, value in custom_parameters.items():
                    if name[0] == '_':
                        continue
                    param_name = 'custom_%s'% name
                    if getattr(record, param_name) == value:
                        record_shall_be_remained = True
                        break
                return record_shall_be_remained
        else:
            raise ValueError("Unknown filter logic")
        self._entities = list(filter(filter_function, self._entities))

    def filter_by_project(self, project):
        """
        Remains only records that belong to a given project

        :param project: A project that is used as filtration criterion
        """
        self._entities = list(filter(lambda record: record.project.id == project.id, self._entities))

    def filter_by_hashtag_list(self, hashtag_list, hashtag_logic):
        """
        Filters all records using the hashtag list

        :param hashtag_list: list of all hashtags
        :param hashtag_logic: the applied logic
        """
        if hashtag_logic == 'and':
            record_list = {record.id for record in self.entities}
        elif hashtag_logic == 'or':
            record_list = set()
        else:
            raise ValueError("Bad hashtag logic")
        hashtag_dictionary = {
            record.id: [hashtag.id for hashtag in record.hashtags]
            for record in self.entities
        }
        for hashtag in hashtag_list:
            local_record_list = {
                record.id for record in self.entities
                if hashtag.id in hashtag_dictionary[record.id]
            }
            if hashtag_logic == 'and':
                record_list &= local_record_list
            if hashtag_logic == 'or':
                record_list |= local_record_list
        if len(hashtag_list) == 0 and hashtag_logic == 'and':
            record_list = set()
        self._entities = list(filter(lambda record: record.id in record_list, self._entities))

    def filter_by_date_from_records(self, reference_record_list, date_from, date_to):
        """
        Remains only such records that lies within a given time interval relatively to at least one record from the
        record list

        :param reference_record_list: list of reference records
        :param date_from: the record start date
        :param date_to: the record finish date
        """
        reference_times = [
            reference_record.datetime
            for reference_record in reference_record_list
            if reference_record.datetime is not None
        ]
        def filter_function(record):
            """
            Defines whether a given record passes through the record list or not

            :param record: the record to test
            :return: True if the record passes through the record list, False otherwise
            """
            if record.datetime is None:
                return False
            relative_times = [
                record.datetime - reference_time
                for reference_time in reference_times
                if record.datetime >= reference_time
            ]
            if len(relative_times) == 0:
                return date_to is None  # Pass if cond. (2) is not applicable
            minimum_relative_time = min(relative_times)
            record_is_passed = True
            if date_from is not None:
                record_is_passed = record_is_passed and minimum_relative_time >= date_from
            if date_to is not None:
                record_is_passed = record_is_passed and minimum_relative_time < date_to
            return record_is_passed
        self._entities = list(filter(filter_function, self._entities))
