from datetime import datetime, timedelta

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
                    self._entities.append(parent_category)
                    current_date += timedelta(days=1)
                    alias = alias[:-1] + chr(ord(alias[-1]) + 1)
                    if alias[-1] == "{":
                        alias = alias[:-1] + "aa"
                    index += 1

    def sort(self):
        self._entities = sorted(self._entities,
                                key=lambda record: record.datetime
                                if record.datetime is not None
                                else datetime(1900, 1, 1))  # NULLS first!

    def clone(self):
        return self.__class__(self._user_set_object, self._project_set_object, _entity_list=self._entities)

    def filter_by_parent_category(self, parent_category):
        self._entities = list(filter(lambda record: record.parent_category.id == parent_category.id, self._entities))

    def filter_by_datetime(self, complex_interval):
        """
        Applies filtration by the datetime

        :param complex_interval: an instance of the ComplexInterval value that denotes what to use
        """
        self._entities = list(filter(
            lambda record: record.datetime is not None and record.datetime in complex_interval, self._entities
        ))

    def filter_by_types(self, types):
        """
        Apply filtration by possible types

        :param types: an iterable object containing all valid types
        """
        self._entities = list(filter(lambda record: record.type in types, self._entities))

    def filter_by_name(self, name):
        """
        Filter only those records which name starts from a given line

        :param name: the record name
        """
        self._entities = list(filter(
            lambda record: record.type == LabjournalRecordType.service and record.name.startswith(name), self._entities
        ))
