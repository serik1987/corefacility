from datetime import datetime

from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import DataRecord, RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_file import File, FileSet
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityFieldInvalid, \
    EntityFieldRequiredException, EntityDuplicatedException

from .labjournal_test_mixin import LabjournalTestMixin
from .base_test_class import BaseTestClass
from .entity_objects.labjournal_file_object import LabjournalFileObject
from ..data_providers.field_value_providers import put_stages_in_provider, string_provider


class TestLabjournalFile(LabjournalTestMixin, BaseTestClass):
    """
    Test routines for the labjournal File entity
    """

    _entity_object_class = LabjournalFileObject
    """ Class of an auxiliary object that manipulates the labjournal file for testing purpose """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_base_environment()
        root_record = RootCategoryRecord(project=cls.optical_imaging)
        cls.sample_category = root_record.children[0]
        sample_category_children = cls.sample_category.children
        sample_category_children.types = [LabjournalRecordType.data]
        records = sample_category_children[0:2]
        cls.sample_record = records[0]
        cls.another_record = records[1]
        LabjournalFileObject._default_create_kwargs['record'] = cls.sample_record

    def setUp(self):
        self.sample_category = TestLabjournalFile.sample_category
        self.sample_record = TestLabjournalFile.sample_record
        self.another_record = TestLabjournalFile.another_record

    @parameterized.expand(put_stages_in_provider([(None,),]))
    def test_record_field_positive(self, technical, mode):
        """
        Positive test for the 'record' field

        :param technical: for service use only
        :param mode: one out of four basic testing modes
        """
        labjournal_file = File(
            record=self.sample_record,
            name="neurons.dat"
        )
        if mode == self.TEST_CHANGE_CREATE_AND_LOAD:
            labjournal_file.record = self.another_record
        labjournal_file.create()
        if mode == self.TEST_CREATE_CHANGE_AND_LOAD:
            labjournal_file.record = self.another_record
            labjournal_file.update()
        labjournal_file = FileSet().get(labjournal_file.id)
        if mode == self.TEST_CREATE_LOAD_AND_CHANGE:
            labjournal_file.record = self.another_record
        if mode == self.TEST_CREATE_AND_LOAD:
            expected_record = self.sample_record
        else:
            expected_record = self.another_record
        self.assertRecordEquals(labjournal_file.record, expected_record)

    def test_record_field_root_parent(self):
        """
        Tests the 'record' field for assignment of the root category child
        """
        parent_category = RootCategoryRecord(project=self.optical_imaging)
        record = DataRecord(
            parent_category=parent_category,
            datetime=datetime(2024, 9, 13, 9, 17),
            alias="sample",
        )
        record.create()
        labjournal_file = File(
            record=record,
            name="neurons.dat",
        )
        labjournal_file.create()
        labjournal_file = FileSet().get(labjournal_file.id)
        self.assertRecordEquals(labjournal_file.record, record)

    @parameterized.expand([(LabjournalRecordType.service,), (LabjournalRecordType.category,),])
    def test_record_field_non_native(self, record_type):
        """
        Tests whether assignment of non-native category is OK
        """
        sample_category_children = self.sample_category.children
        sample_category_children.types = [record_type]
        sample_record = sample_category_children[0]
        with self.assertRaises(EntityFieldInvalid, msg="Invalid value was successfully assigned to the category field"):
            File(record=sample_record, name="neurons.dat")

    def test_record_field_flush(self):
        """
        Tests whether the 'record' field can be flushed
        """
        labjournal_file = File(record=self.sample_record, name="neurons.dat")
        labjournal_file.create()
        with self.assertRaises(EntityFieldInvalid, msg="The 'record' field can't be flushed by assignment of None"):
            labjournal_file.record = None
            labjournal_file.update()

    def test_record_field_required(self):
        """
        Tests that the 'record' field is required
        """
        labjournal_file = File(name="neurons.dat")
        with self.assertRaises(EntityFieldRequiredException, msg="The 'record' field is required"):
            labjournal_file.create()

    def test_different_records_interfere(self):
        """
        Tests whether different files attached to different records interfere to each other
        """
        file1 = File(record=self.sample_record, name="neurons.dat")
        file2 = File(record=self.another_record, name="neurons.dat")
        file1.create()
        file2.create()
        file_set = FileSet()
        file1 = file_set.get(file1.id)
        file2 = file_set.get(file2.id)
        self.assertRecordEquals(file1.record, self.sample_record)
        self.assertEquals(file1.name, "neurons.dat", "File name was corrupted")
        self.assertRecordEquals(file2.record, self.another_record)
        self.assertEquals(file2.name, "neurons.dat", "File name was corrupted")

    @parameterized.expand(string_provider(min_length=1, max_length=256))
    def test_name_field(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Provides a standard test for the 'name' field

        :param initial_value: the first value to assign
        :param final_value: the second value to assign
        :param exception_to_throw: an exception that is expected or None is no exception is expected
        :param route_number: one out of four basic routes
        """
        self._test_field('name', initial_value, final_value, exception_to_throw, route_number)

    def test_name_field_required(self):
        """
        Tests whether the name field is required
        """
        labjournal_file = File(record=self.sample_record)
        with self.assertRaises(EntityFieldRequiredException, msg="The 'name' field must be required"):
            labjournal_file.create()

    def test_name_field_interfere(self):
        """
        Tests whether two files with different names can be attached to the same record
        """
        file1 = File(record=self.sample_record, name="neurons.dat")
        file2 = File(record=self.sample_record, name="behavior.avi")
        file1.create()
        file2.create()
        file_container = FileSet()
        file1 = file_container.get(file1.id)
        file2 = file_container.get(file2.id)
        self.assertRecordEquals(file1.record, self.sample_record)
        self.assertEquals(file1.name, "neurons.dat", "The file name was corrupted")
        self.assertRecordEquals(file2.record, self.sample_record)
        self.assertEquals(file2.name, "behavior.avi", "The file name was corrupted")

    def test_path_field_read_only(self):
        """
        Ensures that the 'path' field is read-only
        """
        self._test_read_only_field('path', ValueError)

    def test__file_duplication(self):
        """
        Tests whether two files with the same name can be attached to the same record
        """
        file1 = File(record=self.sample_record, name="neurons.dat")
        file2 = File(record=self.sample_record, name="neurons.dat")
        file1.create()
        with self.assertRaises(EntityDuplicatedException, msg="The labjournal file duplication must be prohibited"):
            file2.create()

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        """
        self.assertRecordEquals(entity.record, self.sample_record)
        self.assertEquals(entity.name, "neurons.dat", "Bad filename")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly changed during the call of the entity_object.change_entity_fields()
        method

        :param entity: the entity to check
        """
        self.assertRecordEquals(entity.record, self.sample_record)
        self.assertEquals(entity.name, "glia.dat", "Bad filename")

    def _check_field_consistency(self, obj):
        """
        Checks that all entity fields are correctly passed through the database

        :param obj: the entity object
        """
        self.assertRecordEquals(obj.entity.record, self.sample_record)
        self.assertEquals(obj.entity.name, obj.entity_fields['name'], "File name inconsistency")

    def assertRecordEquals(self, actual_record, expected_record):
        """
        Checks whether the 'record' field was properly stored.
        The method deals with default data only.

        :param actual_record: the record within the File object
        :param expected_record: the record that is expected to exist
        """
        self.assertIsInstance(actual_record, DataRecord, "Bad value for 'record' field")
        self.assertEquals(actual_record.id, expected_record.id, "Bad sample record")
        self.assertEquals(actual_record.parent_category.id, expected_record.parent_category.id,
                          "Bad parent category")
        self.assertEquals(actual_record.project.id, expected_record.project.id,
                          "Bad project")
        self.assertEquals(actual_record.parent_category.base_directory,
                          expected_record.parent_category.base_directory, "Bad base directory")


del BaseTestClass
