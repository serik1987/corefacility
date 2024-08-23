from datetime import timedelta, datetime

from django.utils.dateparse import parse_datetime
from parameterized import parameterized

from .base_test_class import BaseTestClass
from .labjournal_test_mixin import LabjournalTestMixin
from .entity_objects.labjournal_record_object import LabjournalRecordObject, RECORD_TYPES, RECORD_TYPE_VALUES, \
    RELATIVE_TIMES

from ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.project import Project
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record import CategoryRecord
from ..data_providers.labjournal_record_provider import labjournal_record_provider, parent_category_change_provider, \
    alias_change_provider, datetime_change_provider, checked_change_provider, comments_change_provider, \
    name_change_provider, base_directory_provider
from ...entity.labjournal_record.data_record import DataRecord
from ...entity.labjournal_record.record_set import RecordSet
from ...entity.labjournal_record.service_record import ServiceRecord
from ...exceptions.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException, EntityFieldInvalid
from ...models import LabjournalRecord, LabjournalCheckedRecord
from ...models.enums.labjournal_record_type import LabjournalRecordType


class TestLabjournalRecord(LabjournalTestMixin, BaseTestClass):
    """
    Provides testing the labjournal record
    """

    _entity_object_class = LabjournalRecordObject

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_base_environment()

    @parameterized.expand(labjournal_record_provider())
    def test_object_creating_default_comphrehensive(self,
                                                    parent_category,
                                                    level,
                                                    project,
                                                    alias,
                                                    relative_time,
                                                    checked,
                                                    user_identity,
                                                    testing_identity,
                                                    record_type,
                                                    comments):
        """
        Provides a comprehensive variant of the test_object_creating_default

        :param parent_category: None to test the root category, 'root' to test the record inside the root category
            'no_root' to test the category inside another type of the category
        :param level: nesting level of the record
        :param project: related project
        :param alias: the record alias, if applicable
        :param relative_time: 'hour', 'day', 'year' or 'inf' (will be used to set an absolute time
        :param checked: True if the record has been checked by the user, False otherwise
        :param user_identity: 'leader' if the record has been created by the group leader, 'no_leader' otherwise
        :param testing_identity: 'leader' if the record was read by the group leader, 'no_leader' otherwise
        :param record_type: a string representing the record type: 'category' for category, 'data' for data,
                'service' for service
        :param comments: additional record comments
        """
        entity_object = self.get_entity_object_class()(
            parent_category=parent_category,
            level=level,
            project=project,
            alias=alias,
            relative_time=relative_time,
            checked=checked,
            user=user_identity,
            type=record_type,
            comments=comments,
        )
        self._check_creating_state_comprehensive(entity_object.entity, parent_category)
        self._check_entity_fields_comprehensive(
            entity_object.entity,
            parent_category,
            level,
            project,
            alias,
            relative_time,
            checked,
            user_identity,
            None,
            record_type,
            comments,
        )
        with self.assertRaises(EntityOperationNotPermitted, msg="Can't change non-saved entity"):
            entity_object.entity.update()
        with self.assertRaises(EntityOperationNotPermitted, msg="Can't delete the non-saved entity"):
            entity_object.entity.delete()
        if isinstance(entity_object.entity, RootCategoryRecord):
            with self.assertRaises(EntityOperationNotPermitted, msg="Can't create new root record"):
                entity_object.create_entity()
        else:
            entity_object.create_entity()

    @parameterized.expand(labjournal_record_provider())
    def test_object_created_default_comprehensive(self,
                                                  parent_category,
                                                  level,
                                                  project,
                                                  alias,
                                                  relative_time,
                                                  checked,
                                                  user_identity,
                                                  testing_identity,
                                                  record_type,
                                                  comments):
        """
        Provides a comprehensive variant of the test_object_created_default

        :param parent_category: None to test the root category, 'root' to test the record inside the root category
            'no_root' to test the category inside another type of the category
        :param level: nesting level of the record
        :param project: related project
        :param alias: the record alias, if applicable
        :param relative_time: 'hour', 'day', 'year' or 'inf' (will be used to set an absolute time
        :param checked: True if the record has been checked by the user, False otherwise
        :param user_identity: 'leader' if the record has been created by the group leader, 'no_leader' otherwise
        :param testing_identity: 'leader' if the record was read by the group leader, 'no_leader' otherwise
        :param record_type: a string representing the record type: 'category' for category, 'data' for data,
                'service' for service
        :param comments: additional record comments
        """
        entity_object = self.get_entity_object_class()(
            parent_category=parent_category,
            level=level,
            project=project,
            alias=alias,
            relative_time=relative_time,
            checked=checked,
            user=user_identity,
            type=record_type,
            comments=comments,
        )
        if parent_category is None:
            with self.assertRaises(EntityOperationNotPermitted, msg="No extra root records can be created"):
                entity_object.create_entity()
        else:
            entity_object.create_entity()
            self._check_created_state_comprehensive(entity_object.entity, parent_category)
            self._check_entity_fields_comprehensive(
                entity_object.entity,
                parent_category,
                level,
                project,
                alias,
                relative_time,
                checked,
                user_identity,
                None,
                record_type,
                comments
            )
            self._check_relative_time(entity_object.entity, True, relative_time)
        with self.assertRaises(EntityOperationNotPermitted, msg="Can't create the entity that is already created"):
            entity_object.create_entity()
        with self.assertRaises(EntityOperationNotPermitted, msg="Can't update the created entity"):
            entity_object.entity.update()

    @parameterized.expand(labjournal_record_provider())
    def test_object_created_and_loaded_comprehensive(self,
                                                     parent_category,
                                                     level,
                                                     project,
                                                     alias,
                                                     relative_time,
                                                     checked,
                                                     user_identity,
                                                     testing_identity,
                                                     record_type,
                                                     comments):
        """
        Provides a comprehensive variant of the test_object_created_and_loaded_default

        :param parent_category: None to test the root category, 'root' to test the record inside the root category
            'no_root' to test the category inside another type of the category
        :param level: nesting level of the record
        :param project: related project
        :param alias: the record alias, if applicable
        :param relative_time: 'hour', 'day', 'year' or 'inf' (will be used to set an absolute time
        :param checked: True if the record has been checked by the user, False otherwise
        :param user_identity: 'leader' if the record has been created by the group leader, 'no_leader' otherwise
        :param testing_identity: 'leader' if the record was read by the group leader, 'no_leader' otherwise
        :param record_type: a string representing the record type: 'category' for category, 'data' for data,
                'service' for service
        :param comments: additional record comments
        """
        record_set = RecordSet()
        entity_object = self.get_entity_object_class()(
            parent_category=parent_category,
            level=level,
            project=project,
            alias=alias,
            relative_time=relative_time,
            checked=checked,
            user=user_identity,
            type=record_type,
            comments=comments,
        )
        if parent_category is not None:
            entity_object.create_entity()
        if parent_category is None:
            entity_object.reload_entity()
            entity_object.entity.comments = comments
            entity_object.entity.update()
            entity_object.reload_entity()
            record = entity_object.entity
        else:
            record_set.user = entity_object.get_user_context(entity_object.entity.project, 'leader')
            record = record_set.get(entity_object.id)
            record.checked = True
            record.update()
            record_set.user = entity_object.get_user_context(entity_object.entity.project, testing_identity)
            record = record_set.get(entity_object.id)
        self._check_loaded_state_comprehensive(entity_object, record)
        self._check_entity_fields_comprehensive(
            record,
            parent_category,
            level,
            project,
            alias,
            relative_time,
            checked,
            user_identity,
            testing_identity,
            record_type,
            comments
        )
        self._check_relative_time(record, False, relative_time)
        with self.assertRaises(EntityOperationNotPermitted, msg="The record duplicate has been successfully created"):
            record.create()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="If the entity has been already created, it can't be updated"):
            record.update()

    @parameterized.expand(labjournal_record_provider())
    def test_object_created_and_deleted_comprehensive(self,
                                                      parent_category,
                                                      level,
                                                      project,
                                                      alias,
                                                      relative_time,
                                                      checked,
                                                      user_identity,
                                                      testing_identity,
                                                      record_type,
                                                      comments):
        """
        Provides a comprehensive way of the test_object_created_and_deleted test

        :param parent_category: None to test the root category, 'root' to test the record inside the root category
            'no_root' to test the category inside another type of the category
        :param level: nesting level of the record
        :param project: related project
        :param alias: the record alias, if applicable
        :param relative_time: 'hour', 'day', 'year' or 'inf' (will be used to set an absolute time
        :param checked: True if the record has been checked by the user, False otherwise
        :param user_identity: 'leader' if the record has been created by the group leader, 'no_leader' otherwise
        :param testing_identity: 'leader' if the record was read by the group leader, 'no_leader' otherwise
        :param record_type: a string representing the record type: 'category' for category, 'data' for data,
                'service' for service
        :param comments: additional record comments
        """
        record_object = self.get_entity_object_class()(
            parent_category=parent_category,
            level=level,
            project=project,
            alias=alias,
            relative_time=relative_time,
            checked=checked,
            user=user_identity,
            type=record_type,
            comments=comments,
        )
        if parent_category is None:
            record_object.reload_entity()
            with self.assertRaises(EntityOperationNotPermitted, msg="Attempt to delete the root record"):
                record_object.entity.delete()
        else:
            record_object.create_entity()
            record_object.entity.delete()
            self.assertIsNone(record_object.entity.id, "The entity ID must be cleared when the entity is deleted")
            with self.assertRaises(EntityOperationNotPermitted, msg="Can't create deleted entity"):
                record_object.create_entity()
            with self.assertRaises(EntityOperationNotPermitted, msg="Can't change the deleted entity"):
                record_object.entity.comments = "Sample"
                record_object.entity.update()
            with self.assertRaises(EntityOperationNotPermitted, msg="Can't delete the deleted entity"):
                record_object.entity.delete()
            with self.assertRaises(EntityNotFoundException, msg="The deleted entity still exists in the database"):
                record_object.reload_entity()
            self.assertEquals(LabjournalRecord.objects.filter(id=record_object.id).count(), 0,
                              "The deleted entity still exists in the core_application_labjournalrecord")
            self.assertEquals(LabjournalCheckedRecord.objects.filter(record_id=record_object.id).count(), 0,
                              "The deleted entity still exists in the core_application_labjournalcheckedrecord")
            if level == 3:
                record_set = RecordSet()
                parent_record = record_set.get(record_object.entity.parent_category.id)
                self.assertIsNone(parent_record.datetime,
                                  "Date and time of the parent category was not modified during the record delete")
                self.assertIsNone(parent_record.finish_time,
                                  "Finish time of the parent category was not modified during the record delete")

    @parameterized.expand(parent_category_change_provider())
    def test_change_parent_category_positive(self,
                                             parent_category,
                                             level,
                                             project,
                                             user_context,
                                             checked,
                                             record_type,
                                             change_parent_category_to,
                                             change_level_to,
                                             change_project_to,
                                             change_mode,
                                             result,
                                             expected_check
                                             ):
        """
        Tests whether the parent category can be properly changed to a given value

        :param parent_category: initial parent category
        :param level: initial level
        :param project: initial project
        :param user_context: the changing user context (checked parameter will always be checked by the leader)
        :param checked: Whether the user has checked the field
        :param record_type: type of the record to check
        :param change_parent_category_to: new value of the parent category
        :param change_level_to: new value of the level to change
        :param change_project_to: new value of the related project
        :param change_mode: 'on_create' for "change + create + load + assert" testing
                'after_create' for "create + change + update + load + assert" testing
                'after_load' for "create + load + change + update + assert" testing
        :param result: True if the result is required to be success, exception if the exception must be thrown
        """
        record_set = RecordSet()
        if change_parent_category_to is not None:
            new_parent_category = self.get_entity_object_class()().get_parent_category(
                change_parent_category_to,
                change_project_to,
                change_level_to
            )
        else:
            new_parent_category = None
        if parent_category is not None:
            old_parent_category = self.get_entity_object_class()().get_parent_category(
                parent_category,
                project,
                level
            )
        else:
            old_parent_category = None
        if parent_category == 'no_root':
            old_parent_category = record_set.get(old_parent_category.id)

        def wrapped_function():
            record_object = self.get_entity_object_class()(
                parent_category=parent_category,
                level=level,
                project=project,
                alias='sample_record',
                relative_time='hour',
                checked=checked,
                user=user_context,
                type=record_type,
                comments="Это - обычный комментарий!",
            )
            if change_mode == 'on_create':
                record_object.entity.parent_category = new_parent_category
            if parent_category is None:
                record_object.reload_entity()
                record_object.entity.comments = "Это - обычный комментарий!"
                record_object.entity.update()
            else:
                record_object.create_entity()
            if change_mode == 'after_create':
                record_object.entity.parent_category = new_parent_category
                record_object.entity.update()
            record_object.reload_entity()
            if change_mode == 'after_load':
                record_object.entity.parent_category = new_parent_category
                record_object.entity.update()
            return record_object.entity

        if isinstance(result, bool) and result:
            record = wrapped_function()
            self.assertEquals(record.parent_category.id, new_parent_category.id,
                              "Bad parent category was assigned to the record")
            self.assertEquals(record.level, change_level_to,
                              "Bad level was calculated during the category change")
            self.assertEquals(record.project.alias, change_project_to,
                              "The record was re-attached to the wrong project during the category change")
            self.assertEquals(record.checked, checked,
                              "The checked field has lost during the category reload")
            self.assertIsInstance(record, RECORD_TYPES[record_type],
                                  "The record class was suddenly changed when the parent category was changed")
            if record.type != LabjournalRecordType.service:
                self.assertEquals(record.alias, 'sample_record',
                                  "Record alias was corrupted when the parent category was changed")
            self.assertEquals(record.comments, "Это - обычный комментарий!",
                              "The record comments were corrupted when the record was changed")
            record_object = self.get_entity_object_class()()
            project_context = record_object.get_project(project)
            record_set.user = record_object.get_user_context(project_context, 'leader')
            record = record_set.get(record.id)
            self.assertEquals(record.checked, expected_check,
                              "The record check status was corrupted during the parent category change")
            if parent_category == 'no_root':
                old_parent_category_v2 = record_set.get(old_parent_category.id)
                self.assertEquals(old_parent_category.datetime, old_parent_category_v2.datetime,
                                  "The category datetime did not restored to its previous value when the"
                                  "record detached from the category")
        else:
            with self.assertRaises(result):
                wrapped_function()

    @parameterized.expand([('data',), ('service',)])
    def test_make_parent_data(self, record_type):
        """
        Tests whether the data or service record can be make as parent

        :param record_type: 'data' for data, 'service' for service
        """
        parent_record = self.get_entity_object_class()(
            parent_category='root',
            project='optical_imaging',
            level=1,
            type=record_type,
            alias=1,
            relative_time='hour',
        )
        parent_record.create_entity()
        with self.assertRaises(EntityFieldInvalid, msg="Only category can be parent category"):
            DataRecord(parent_category=parent_record.entity)
        with self.assertRaises(EntityFieldInvalid, msg="Only category can be parent category"):
            ServiceRecord(parent_category=parent_record.entity)

    @parameterized.expand(alias_change_provider())
    def test_alias_change(self,
                          parent_category,
                          level,
                          record_type,
                          change_alias_to,
                          change_mode,
                          error_thrown):
        """
        Tests whether the alias can be changed correctly

        :param parent_category: the parent category to check
        :param level: the nesting level
        :param record_type: 'data' for the data record, 'service' fpr the service record, 'category' for the category
        :param change_mode: 'on_creating' to change at the time of entity creating, 'after_load' to change the field
            after the entity has been loaded
        :param error_thrown: None if the field change must be successful. Otherwise, an exception that is expected to
            be thrown
        """

        def wrapped():
            record_object = self.get_entity_object_class()(
                parent_category=parent_category,
                level=level,
                project='optical_imaging',
                alias='sample_record',
                relative_time='hour',
                comments="Я родился!",
                checked=False,
                user='no_leader',
                type=record_type,
            )
            if change_mode == 'on_creating':
                record_object.entity.alias = change_alias_to
            if parent_category is not None:
                record_object.create_entity()
            record_object.reload_entity()
            if change_mode == 'after_load':
                record_object.entity.alias = change_alias_to
                record_object.entity.update()
            if parent_category == 'root':
                self.assertIsNone(record_object.entity.parent_category.id, "The parent category must be root")
            else:
                self.assertIsNotNone(record_object.entity.parent_category.id, "The parent category must not be "
                                                                              "root")
            self.assertEquals(record_object.entity.level, level, "Entity level mismatch")
            self.assertEquals(record_object.entity.alias, change_alias_to, "Alias change was unsuccessful")
            self.assertEquals(record_object.entity.comments, "Я родился!",
                              "Comments suddenly changed during the alias change")
            self.assertEquals(record_object.entity.project.alias, 'optical_imaging',
                              "The relating project was suddenly changed during the alias assignment")
            self.assertFalse(record_object.entity.checked,
                             "The record was suddenly checked during the alias assignment")
            self.assertIsInstance(record_object.entity, RECORD_TYPES[record_type],
                                  "The record type was changed during the alias assignment")
        if error_thrown is None:
            wrapped()
        else:
            with self.assertRaises(error_thrown, msg="This test should throw an exception"):
                wrapped()

    @parameterized.expand(datetime_change_provider())
    def test_datetime_change(self,
                             parent_category,
                             level,
                             record_type,
                             change_time_by,
                             change_mode,
                             result,
                             desired_datetime,
                             desired_parent_category_datetime,
                             desired_parent_category_finish_time,
                             desired_relative_time
                             ):
        """
        Whether the datetime field can be correctly changed

        :param parent_category: a cue for the parent category
        :param level: desired entity level
        :param record_type: record type: 'data', 'service' or 'category'
        :param change_time_by: a short cue of what value of the datetime field should be
        :param change_mode: 'on_creating to change the field + create entity, "after_create" to create entity
            + change field + save the entity (in any way, the entity will be reloaded from the database)
        :param result: None if the field change process should be successful, otherwise, class of the desired exception
        :param desired_datetime: new value of the 'datetime' field to be expected
        :param desired_parent_category_datetime: new value of the parent's 'datetime' fieild to be expected
        :param desired_parent_category_finish_time: new value of the parent's 'finish_time' field to be expected
        :param desired_relative_time: new value of the 'relative_time' field to be expected
        """
        record_type = RECORD_TYPES[record_type]
        record_object = self.get_entity_object_class()()
        if parent_category is not None:
            parent_category = record_object.get_parent_category(parent_category, 'optical_imaging', level)
            reference_datetime = parent_category.datetime
        else:
            parent_category = None
            reference_datetime = None
        if reference_datetime is None:
            reference_datetime = datetime(2012, 7, 15, 12, 30)
        if change_time_by == "0":
            new_datetime = reference_datetime
        elif change_time_by != str:
            change_time_by_absolute = RELATIVE_TIMES[change_time_by[1:]]
            if change_time_by[0] == '+':
                new_datetime = reference_datetime + change_time_by_absolute
            elif change_time_by[0] == '-':
                new_datetime = reference_datetime - change_time_by_absolute
            else:
                raise ValueError("This method is not suitable for a given test case")
        else:
            new_datetime = "lkjsfdhgkjfhkjg"
        if desired_datetime is not None:
            desired_datetime = parse_datetime(desired_datetime)
            self.assertEquals(new_datetime, desired_datetime,
                              "The test case is malformed")
        if desired_parent_category_datetime is not None:
            desired_parent_category_datetime = parse_datetime(desired_parent_category_datetime)
        if desired_parent_category_finish_time is not None:
            desired_parent_category_finish_time = parse_datetime(desired_parent_category_finish_time)
        user_context = record_object.get_user_context(self.optical_imaging, 'no_leader')
        record_set = RecordSet()

        def wrapped():
            if parent_category is not None:
                record = record_type(
                    parent_category=parent_category,
                    datetime=reference_datetime,
                    user=user_context,
                    checked=True,
                    comments="Я родился!",
                )
                if not isinstance(record, ServiceRecord):
                    record.alias = 'sample_record'
                if change_mode == 'on_creating':
                    record.datetime = new_datetime
                record.create()
                if change_mode == 'after_create':
                    record.datetime = new_datetime
                    record.update()
                record_set.user = user_context
                record = record_set.get(record.id)
            else:
                record = record_set.get_root(self.optical_imaging)
                record.datetime = new_datetime
                record.update()
            return record
        if result is None:
            record = wrapped()
            self.assertEquals(record.parent_category.id, parent_category.id,
                              "The parent category did not stored correctly")
            self.assertEquals(record.level, level, "The record level did not stored")
            self.assertIsInstance(record, record_type, "The record type mismatch during the save")
            self.assertEquals(record.project.alias, 'optical_imaging', "The project retrieval mismatch")
            if not isinstance(record, ServiceRecord):
                self.assertEquals(record.alias, 'sample_record', "Alias mismatch")
            self.assertTrue(record.checked, "The checked property mismatch")
            self.assertEquals(record.comments, "Я родился!", "Record comments mismatch")
            self.assertEquals(record.datetime, desired_datetime,
                              "The record datetime did not stored correctly")
            self.assertEquals(record.parent_category.datetime, desired_parent_category_datetime,
                              "The parent category datetime did not updated correctly")
            self.assertEquals(record.parent_category.finish_time, desired_parent_category_finish_time,
                              "The parent category finish time did not updated correctly")
            self.assertEquals(record.relative_time, desired_relative_time,
                              "The relative time did not correctly computed during the record loading")
        else:
            with self.assertRaises(result):
                wrapped()

    @parameterized.expand(checked_change_provider())
    def test_checked_change(self,
                            parent_category,
                            level,
                            record_type,
                            first_user,
                            first_check,
                            second_user,
                            second_check,
                            result_overall,
                            result_no_leader,
                            result_leader):
        """
        Tests whether the 'checked' field is stored and/or retrieved correctly

        :param parent_category: a cue for the parent category
        :param level: the record nesting level
        :param record_type: One of the following record types: 'data', 'service', 'category'
        :param first_user: the very first user that checked the record
        :param first_check: value of the very first user
        :param second_user: the very second user that has checked the record
        :param second_check: value of the very second check
        :param result_overall: None for successful check, otherwise the desired exception is expected to be
        :param result_no_leader: the check status for the 'no_leader' user
        :param result_leader: the check status for the 'leader' user
        """
        record_set = RecordSet()
        record_object = self.get_entity_object_class()(
            parent_category=parent_category,
            level=level,
            project='optical_imaging',
            alias='sample_record',
            relative_time='hour',
            checked=first_check,
            user=first_user,
            type=record_type,
            comments="Я родился",
        )
        second_user = record_object.get_user_context(self.optical_imaging, second_user)
        no_leader = record_object.get_user_context(self.optical_imaging, 'no_leader')
        leader = record_object.get_user_context(self.optical_imaging, 'leader')
        if parent_category is None:
            record_object.reload_entity()
            record = record_object.entity
        else:
            record_object.create_entity()
            record_set.user = second_user
            record = record_set.get(record_object.entity.id)
        if result_overall is None:
            record.checked = second_check
            record.update()
            record_set.user = no_leader
            record = record_set.get(record.id)
            self.assertEquals(record.checked, result_no_leader,
                              "The check status has been corrupted")
            record_set.user = leader
            record = record_set.get(record.id)
            self.assertEquals(record.checked, result_leader,
                              "The check status has been corrupted")
        else:
            with self.assertRaises(AttributeError):
                record.checked = second_check
                record.update()

    @parameterized.expand(comments_change_provider())
    def test_comments_change(self, parent_category, level, record_type, comments, change_mode):
        """
        Tests whether the record comments are modified correctly

        :param parent_category: the cue for the parent category
        :param level: the nesting level
        :param record_type: one of the following record types: 'data', 'service', 'category'
        :param comments: comments to set up
        :param change_mode: 'on_creating', 'after_created', 'after_load' depending on when to change the comments
        """
        record_object = self.get_entity_object_class()(
            parent_category=parent_category,
            level=level,
            project='optical_imaging',
            alias='sample_record',
            relative_time='hour',
            checked=False,
            user='leader',
            type=record_type,
            comments="Первоначальное значение поля",
        )
        if change_mode == 'on_creating':
            record_object.entity.comments = comments
        old_parent_category = None
        if parent_category is None:
            record_object.reload_entity()
        else:
            old_parent_category = record_object.entity.parent_category
            record_object.create_entity()
        if change_mode == 'after_create':
            record_object.entity.comments = comments
            record_object.entity.update()
        record_object.reload_entity()
        if change_mode == 'after_load':
            record_object.entity.comments = comments
            record_object.entity.update()
        if parent_category is None:
            self.assertEquals(record_object.entity.comments, comments, "The record comments were not stored correctly")
        else:
            self.assertIsInstance(record_object.entity, RECORD_TYPES[record_type],
                                  "The record type was damaged")
            self.assertEquals(record_object.entity.parent_category.id, old_parent_category.id,
                              "The parent category was damaged")
            self.assertEquals(record_object.entity.level, level, "The level was damaged")
            self.assertEquals(record_object.entity.project.alias, 'optical_imaging',
                              "The relating project was damaged")
            if record_type != 'service':
                self.assertEquals(record_object.entity.alias, 'sample_record',
                                  "The entity alias was damaged")
            self.assertEquals(record_object.entity.checked, False, "The checked field was damaged")
            self.assertEquals(record_object.entity.comments, comments,
                              "The record comments were not stored correctly")

    @parameterized.expand(name_change_provider())
    def test_name_change(self, parent_category, level, record_type, name, result):
        """
        Tests how the record name can be changed

        :param parent_category: a cue for the parent category
        :param level: nesting level
        :param record_type: a cue for the record type
        :param name: new value of the record name
        :param result: None if the result is expected to be successful. Otherwise, the error that is expected to
            be thrown
        """
        def wrapped():
            entity_object = self.get_entity_object_class()(
                parent_category=parent_category,
                level=level,
                project='optical_imaging',
                alias='sample_record',
                relative_time='hour',
                checked=True,
                user='leader',
                type=record_type,
                comments=None,
            )
            if parent_category is None:
                entity_object.reload_entity()
            else:
                entity_object.create_entity()
            entity_object.entity.name = name
            entity_object.entity.update()
            entity_object.reload_entity()
            entity_object.reload_entity()
            return entity_object.entity
        if result is None:
            record = wrapped()
            parent_category = self.get_entity_object_class()()\
                .get_parent_category(parent_category, 'optical_imaging', level)
            self.assertEquals(record.parent_category.id, parent_category.id,
                              "Parent category was damaged")
            self.assertEquals(record.level, level, "The level was damaged")
            self.assertEquals(record.project.alias, 'optical_imaging', "The relating project was damaged")
            self.assertEquals(record.checked, True, "The check was damaged")
            self.assertIsInstance(record, ServiceRecord, "The record type was damaged")
            self.assertIsNone(record.comments, "The record comments were damaged")
            self.assertEquals(record.name, name, "The record name doesn't store correctly")
        else:
            with self.assertRaises(result, msg="This is a negative test case!"):
                wrapped()

    @parameterized.expand(base_directory_provider())
    def test_base_directory(self, parent_category, level, record_type, base_directory, result):
        """
        Provides a base directory test

        :param parent_category: cue for the parent category
        :param level: the nesting level
        :param record_type: cue for the record type
        :param base_directory: new value for the base directory
        :param result: None if such a change is expected to be successful. Otherwise, class of an exception that
            is expected to be thrown
        """
        def wrapped():
            record_object = self.get_entity_object_class()(
                parent_category=parent_category,
                level=level,
                project='the_rabbit_project',
                alias='sample_record',
                relative_time='day',
                checked=True,
                user='leader',
                type=record_type,
            )
            if parent_category is None:
                record_object.reload_entity()
            else:
                record_object.create_entity()
            record_object.entity.base_directory = base_directory
            record_object.entity.update()
            record_object.reload_entity()
            return record_object
        if result is None:
            record_object = wrapped()
            if parent_category is not None:
                self.assertEquals(
                    record_object.entity.parent_category.id,
                    record_object.get_parent_category(parent_category, 'the_rabbit_project', level).id,
                    "The parent category was damaged"
                )
                self.assertEquals(record_object.entity.level, level, "Nesting level damage")
                self.assertEquals(record_object.entity.project.alias, 'the_rabbit_project',
                                  "Related project damage")
                self.assertEquals(record_object.entity.alias, 'sample_record', "Alias damage")
                self.assertEquals(record_object.entity.checked, True, "Checked damage")
                self.assertIsInstance(record_object.entity, CategoryRecord, "Bad record type")
            self.assertEquals(record_object.entity.base_directory, base_directory, "Bad base directory")
        else:
            self.assertRaises(result, wrapped)

    @parameterized.expand([
        ('project', CategoryRecord, 'optical_imaging'),
        ('level', CategoryRecord, 10),
        ('project', DataRecord, 'optical_imaging'),
        ('level', ServiceRecord, 10),
        ('type', DataRecord, LabjournalRecordType.service),
        ('level', DataRecord, 10),
        ('type', CategoryRecord, LabjournalRecordType.service),
        ('type', RootCategoryRecord, LabjournalRecordType.service),
        ('level', RootCategoryRecord, 10),
        ('relative_time', CategoryRecord, timedelta()),
        ('relative_time', DataRecord, timedelta()),
        ('relative_time', ServiceRecord, timedelta()),
        ('finish_time', CategoryRecord, datetime.now())
    ])
    def test_read_only_field(self, name, record_type, value):
        """
        This is the base class for all read-only tests
        """
        if name == 'project':
            value = getattr(self, value)
        with self.assertRaises(ValueError, msg="The read-only field has been successfully changed"):
            record_type(**{name: value})

    @parameterized.expand([
        ('relative_time', RootCategoryRecord, timedelta()),
        ('finish_time', DataRecord, datetime.now()),
        ('finish_time', ServiceRecord, datetime.now()),
    ])
    def test_unexistent_field(self, name, record_type, value):
        """
        Tests any non-existent fields that are not covered by all previous tests
        """
        with self.assertRaises(AttributeError, msg="The field must be non-existent but this is successfully accessed"):
            record_type(**{name: value})

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertIsInstance(entity.parent_category, RootCategoryRecord, "Parent category is not the root one")
        self.assertIsInstance(entity.project, Project, "The project was not saved")
        self.assertEquals(entity.project.alias, 'the_rabbit_project', "Bad project alias")
        self.assertEquals(entity.project.id, entity.parent_category.project.id,
                          "Project of the entity is not the same as project of the parent entity")
        self.assertEquals(entity.level, 1, "Bad entity level")
        self.assertIsNone(entity.datetime, "Datetime of the newly created category should be zero")
        self.assertFalse(entity.checked, "The record must be unchecked")
        self.assertIsInstance(entity, CategoryRecord, "The entity must be CategoryRecord")
        self.assertEquals(entity.type, LabjournalRecordType.category, "Bad record type")
        self.assertEquals(entity.comments, "Прочая информация об указанной записи",
                          "The entity comments were stored incorrectly")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly changed during the call of the entity_object.change_entity_fields()
        method

        :param entity: the entity to check
        """
        self.assertEquals(entity.alias, "B", "Entity alias mismatch")
        self.assertEquals(entity.checked, True, "Entity check mismatch")

    def _check_reload(self, obj):
        """
        Checks whether the entity is successfully and correctly reloaded.

        :param obj: the entity object within which the entity was reloaded
        :return: nothing
        """
        self.assertIsInstance(obj.entity, CategoryRecord, "Unexpected entity class")
        self.assertEquals(obj.entity.id, obj.id, "The entity ID was not properly retrieved")
        self.assertEquals(obj.entity.state, "loaded", "The entity state is not 'loaded' when the entity is loaded")
        self._check_field_consistency(obj)

    def _check_field_consistency(self, obj):
        for name, expected_value in obj.entity_fields.items():
            actual_value = getattr(obj.entity, name)
            if name == 'parent_category' and expected_value == 'root':
                self.assertIsInstance(actual_value, RootCategoryRecord,
                                      "The parent category must be an instance of the RootCategoryRecord for"
                                      "a given test case")
            elif name == 'parent_category' and expected_value == 'no_root':
                self.assertIsInstance(actual_value, CategoryRecord,
                                      "The parent category must be an instance of the CategoryRecord")
                self.assertNotIsInstance(actual_value, RootCategoryRecord,
                                         "The parent category did not changed")
            elif name == 'project':
                self.assertEquals(actual_value.alias, expected_value,
                                  "The record suddenly changed its related project")
            elif name == 'user':
                expected_user = obj.get_user_context(obj.entity.project, expected_value)
                self.assertEquals(actual_value.id, expected_user.id,
                                  "The user context of the Record must be set automatically during the loading"
                                  "based on the user context of the RecordSet")
            else:
                self.assertEquals(actual_value, expected_value,
                                  "The entity field '%s' doesn't retrieved correctly" % name)

    def _check_creating_state_comprehensive(self, record, parent_category):
        """
        Checks whether the record state is CREATING

        :param record: the record to check
        :param parent_category: desired parent category
        """
        self.assertIsNone(record.id, "When the record is not stored in the database, its ID must be None")
        if parent_category is None:
            self.assertEquals(record.state, 'found',
                              "This is not possible to create the root record, so RootCategoryRecord() must return"
                              "only FOUND record")
        else:
            self.assertEquals(record.state, 'creating',
                              "The newly creating record should be in the 'creating' state when this is not in "
                              "the database")

    def _check_created_state_comprehensive(self, record, parent_category):
        self.assertIsNotNone(record.id, "When the record is stored in the database an ID must be assigned")
        if parent_category is None:
            self.fail("One extra root category has been successfully created")
        else:
            self.assertEquals(record.state, 'saved', "Bad state after the record has been created")

    def _check_loaded_state_comprehensive(self, record_object, record):
        self.assertEquals(record_object.id, record.id, "Record ID mismatch")
        self.assertEquals(record.state, "loaded", "Bad entity state")

    def _check_entity_fields_comprehensive(self, record, parent_category, level, project, alias, relative_time,
                                             checked, user_identity, testing_identity, record_type, comments):
        """
        Provides a comprehensive check of whether the entity fields were correctly set

        :param record: the record to be tested
        :param parent_category: None to test the root category, 'root' to test the record inside the root category
            'no_root' to test the category inside another type of the category
        :param level: nesting level of the record
        :param project: related project
        :param alias: the record alias, if applicable
        :param relative_time: 'hour', 'day', 'year' or 'inf' (will be used to set an absolute time
        :param checked: True if the record has been checked by the user, False otherwise
        :param user_identity: 'leader' if the record has been created by the group leader, 'no_leader' otherwise
        :param testing_identity: None if the entity is reading by the same user as create it,
            'leader' if the record is reading by the user leader, 'no_leader' if the record doesn't created by the user
            leader
        :param record_type: a string representing the record type: 'category' for category, 'data' for data,
                'service' for service
        :param comments: additional record comments
        """
        if parent_category is None:
            with self.assertRaises(AttributeError, msg="The root record shouldn't have the parent category"):
                print(record.parent_category)
        elif parent_category == 'root':
            self.assertIsInstance(record.parent_category, RootCategoryRecord,
                                  "parent category should be the root record")
        else:
            self.assertNotIsInstance(record.parent_category, RootCategoryRecord,
                                         "Parent category should not be the root record")
        self.assertEquals(record.level, level, "Record level mismatch")
        self.assertEquals(record.project.alias, project, "Record project mismatch")
        if isinstance(record, ServiceRecord):
            with self.assertRaises(AttributeError, msg="Service records don't have alias"):
                record.alias = 'some_field'
        elif isinstance(record, RootCategoryRecord):
            with self.assertRaises(AttributeError, msg="The root record doesn't have alias"):
                print(record.alias)
        else:
            self.assertEquals(record.alias, alias, "Record alias mismatch")
        if isinstance(record, RootCategoryRecord):
            with self.assertRaises(AttributeError, msg="The root record can't be checked"):
                print(record.checked)
            if record.state == 'found':
                with self.assertRaises(RuntimeError, msg="The root record can't be changed when this is in FOUND state"):
                    record.comments = "Я родился!"
            else:
                self.assertEquals(record.comments, comments, "Record comments mismatch")
        else:
            if testing_identity == "leader":
                self.assertTrue(record.checked,
                                "The project leader has checked the record but suddenly sees that the record is "
                                "still unchecked")
            elif testing_identity == "no_leader" and user_identity == "leader":
                self.assertFalse(record.checked,
                                 "The project participant suddenly sees that the record he hasn't checked is"
                                 "indeed checked")
            elif testing_identity == "no_leader" and user_identity == "no_leader":
                self.assertEquals(record.checked, checked,
                                  "The project participant has set the 'checked' state but suddenly see that "
                                  "someone changed this record status (actually only the project leader changed"
                                  "the check status, nobody more)")
            else:
                self.assertEquals(record.checked, checked, "Record check value mismatch")
            self.assertEquals(record.comments, comments, "Record comments mismatch")
        if parent_category is not None:
            self.assertIsNotNone(record.user, "The user context was not set for a particular record")
        self.assertIsInstance(record, RECORD_TYPES[record_type],
                              "Mismatch between the record class and the record type")
        self.assertEquals(record.type, RECORD_TYPE_VALUES[record_type],
                          "Mismatch between the record type and the value of the 'type' field")

    def _check_relative_time(self, record, reload_parent_category, desired_relative_time):
        """
        Checks the relative time of a given record

        :param record: the record which relative time must be checked
        :param reload_parent_category: True if you need to reload the parent category to check the category time
        :param desired_relative_time: A cue for the relative time
        """
        if isinstance(record, CategoryRecord):
            self.assertIsNone(record.datetime, "The field must be empty for the newly created category")
            self.assertIsNone(record.finish_time, "The field must be empty for the newly created category")
        else:
            self.assertIsNotNone(record.datetime, "The field is mandatory for data and service record")
            parent_category = record.parent_category
            if isinstance(parent_category, RootCategoryRecord):
                self.assertIsNone(parent_category.datetime, "Start date for the parent category is always None")
                self.assertIsNone(parent_category.finish_time, "Finish date for the parent category is always None")
                self.assertIsNone(record.relative_time, "The relative time is None when the record is inside "
                                                        "the parent category")
            else:
                if reload_parent_category:
                    record_set = RecordSet()
                    parent_category = record_set.get(parent_category.id)
                self.assertIsNotNone(parent_category.datetime, "The datetime of the parent category should not be "
                                                               "None when non-category object is inside it")
                self.assertIsNotNone(parent_category.finish_time, "The finish time of the parent category should"
                                                                  " not be None when non-category object is inside it")
                self.assertLessEqual(parent_category.datetime, record.datetime,
                                     "The parent category datetime should be less than the record datetime")
                self.assertGreaterEqual(parent_category.finish_time, record.datetime,
                                        "The parent category finish_time should be more than "
                                        "the record finish time")
                relative_time = record.datetime - parent_category.datetime
                self.assertEquals(relative_time, record.relative_time,
                                  "The relative time should be calculated at this stage")
                desired_relative_time = RELATIVE_TIMES[desired_relative_time]
                if relative_time != timedelta():
                    self.assertEquals(relative_time, desired_relative_time,
                                      "Incorrect value was set to the record's datetime field")


del BaseTestClass
