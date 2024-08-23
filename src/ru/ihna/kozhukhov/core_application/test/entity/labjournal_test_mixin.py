from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from ru.ihna.kozhukhov.core_application.models import LabjournalRootRecord, LabjournalRecord
from ru.ihna.kozhukhov.core_application.entity.user import UserSet
from ru.ihna.kozhukhov.core_application.entity.project import ProjectSet
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from ru.ihna.kozhukhov.core_application.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject
from ru.ihna.kozhukhov.core_application.test.entity_set.entity_set_objects.user_set_object import UserSetObject


class LabjournalTestMixin:
    """
    Contains routines for creation and destruction of the test environment
    """

    users = None
    """ All users inside the test environment """

    groups = None
    """ All groups inside the test environment """

    projects = None
    """ All projects inside the test environment """

    optical_imaging = None
    """ The optical imaging project """

    the_rabbit_project = None
    """ The rabbit project """

    current_user = None
    """ The user that we are considering """

    journal_records = None
    """ All records that are used as use cases """

    @classmethod
    def create_base_environment(cls):
        """
        Creates new test environment
        """

        cls.users = UserSetObject()
        cls.groups = GroupSetObject(cls.users)
        cls.projects = ProjectSetObject(cls.groups)

        cls.current_user = UserSet().get('user1')

        project_set = ProjectSet()
        cls.optical_imaging = project_set.get('hhna')
        cls.optical_imaging.alias = 'optical_imaging'
        cls.optical_imaging.name = "Оптическое картирование по внутреннему сигналу"
        cls.optical_imaging.update()

        cls.the_rabbit_project = project_set.get('mnl')
        cls.the_rabbit_project.alias = 'the_rabbit_project'
        cls.the_rabbit_project.name = "Миндалина кроликов"
        cls.the_rabbit_project.update()

        for project in (cls.optical_imaging, cls.the_rabbit_project):
            current_date = datetime(2024, 1, 1)
            category_alias = 'a'
            while current_date <= datetime(2025, 1, 1):
                finish_time = current_date + timedelta(days=1)
                animal_category = LabjournalRecord(
                    parent_category=None,
                    project_id=project.id,
                    level=1,
                    alias=category_alias,
                    datetime=make_aware(current_date),
                    type=LabjournalRecordType.category,
                    finish_time=make_aware(finish_time),
                    base_directory="/data/optical_imaging/" + category_alias
                )
                animal_category.save()
                current_time = current_date
                index = 1
                while current_time <= finish_time:
                    LabjournalRecord(
                        parent_category=animal_category,
                        project_id=project.id,
                        level=2,
                        alias=category_alias + str(index),
                        datetime=make_aware(current_time),
                        type=LabjournalRecordType.data,
                    ) \
                        .save()
                    current_time += timedelta(hours=1)
                    index += 1
                current_time = current_date
                index = 1
                while current_time <= finish_time:
                    LabjournalRecord(
                        parent_category=animal_category,
                        project_id=project.id,
                        level=2,
                        alias=category_alias,
                        datetime=make_aware(current_time),
                        type=LabjournalRecordType.service,
                        name="Служебная запись " + str(index)
                    ) \
                        .save()
                    index += 1
                    current_time += timedelta(hours=1, minutes=30)
                LabjournalRecord(
                    parent_category=animal_category,
                    project_id=project.id,
                    level=2,
                    alias='sample_category',
                    datetime=None,
                    type=LabjournalRecordType.category,
                ) \
                    .save()
                current_date += timedelta(days=14)
                index += 1
                category_alias = category_alias[:-1] + chr(ord(category_alias[-1]) + 1)
                if category_alias[-1] == "{":
                    category_alias = "a" * (len(category_alias) + 1)
