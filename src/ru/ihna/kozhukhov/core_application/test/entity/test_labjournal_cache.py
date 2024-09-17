from datetime import datetime
from sys import getsizeof
from time import time

from django.test import TestCase
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.group import Group
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RootCategoryRecord, DataRecord, CategoryRecord, \
    ServiceRecord, RecordSet
from ru.ihna.kozhukhov.core_application.entity.project import Project
from ru.ihna.kozhukhov.core_application.entity.user import User
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityNotFoundException
from ru.ihna.kozhukhov.core_application.utils import LabjournalCache

def path_category_change_provider():
    data = [
        ('data', 1, 1, "/disclaimer"),
        ('data', 1, 2, "/disclaimer"),
        ('data', 2, 1, "/new/disclaimer"),
        ('data', 2, 2, "/adult/disclaimer"),
        ('data', 3, 1, "/new/rab001/rec001"),
        ('data', 3, 2, "/adult/new/rec001"),
        ('category', 2, 1, "/new/rab001"),
        ('category', 2, 2, "/adult/new"),
        ('category', 1, 1, "/new"),
        ('category', 1, 2, "/adult"),
        ('category', 0, 1, "/"),
        ('category', 0, 2, "/"),
    ]
    return [
        (record_type, record_index, change_category_index, expected_path, flush)
        for (record_type, record_index, change_category_index, expected_path) in data
        for flush in (False, True)
    ]

def find_by_path_provider():
    return [
        ("/", 'category', 0),
        ("/adult", 'category', 1),
        ("/adult/rab001", 'category', 2),
        ("/disclaimer", 'data', 1),
        ("/adult/disclaimer", 'data', 2),
        ("/adult/rab001/rec001", 'data', 3),
    ]

def find_by_path_after_category_change():
    data = [
        (1, '/', None, 'category', 0),
        (1, '/disclaimer', None, 'data', 1),
        (1, '/new', None, 'category', 1),
        (1, '/adult', EntityNotFoundException, None, None),
        (1, '/new/disclaimer', None, 'data', 2),
        (1, '/adult/disclaimer', EntityNotFoundException, None, None),
        (1, '/new/rab001', None, 'category', 2),
        (1, '/adult/rab001', EntityNotFoundException, None, None,),
        (1, '/new/rab001/rec001', None, 'data', 3),
        (1, '/adult/rab001/rec001', EntityNotFoundException, None, None),
        (2, '/', None, 'category', 0),
        (2, '/disclaimer', None, 'data', 1),
        (2, '/adult', None, 'category', 1),
        (2, '/adult/disclaimer', None, 'data', 2),
        (2, '/adult/new', None, 'category', 2),
        (2, '/adult/rab001', EntityNotFoundException, None, None),
        (2, '/adult/new/rec001', None, 'data', 3),
        (2, '/adult/rab001/rec001', EntityNotFoundException, None, None),
    ]
    return [
        (category_to_change, path, exception_to_throw, expected_record_type, expected_record_index, flush)
        for (category_to_change, path, exception_to_throw, expected_record_type, expected_record_index) in data
        for flush in (False, True)
    ]


class TestLabjournalCache(TestCase):
    """
    Provides test routines for the labjournal cache
    """

    @classmethod
    def setUpTestData(cls):
        """
        Runs before all test cases below
        """
        super().setUpTestData()
        cls.sample_user = User(
            login="sergei_kozhukhov",
            name="Сергей",
            surname="Кожухов",
            email="sergei.kozhukhov@ihna.ru",
        )
        cls.sample_user.create()
        cls.sample_group = Group(
            name="Белые зайчики",
            governor=cls.sample_user,
        )
        cls.sample_group.create()
        cls.sample_project = Project(
            alias="white_rabbit",
            name="Исследование обоняния у белых зайчиков",
            root_group=cls.sample_group,
        )
        cls.sample_project.create()
        cls.root_category_record = RootCategoryRecord(project=cls.sample_project)
        cls.sample_record_level_1 = DataRecord(
            parent_category=cls.root_category_record,
            alias="disclaimer",
            datetime=datetime(2024, 9, 16, 3, 28)
        )
        cls.sample_record_level_1.create()
        cls.sample_category = CategoryRecord(
            parent_category=cls.root_category_record,
            alias="adult",
        )
        cls.sample_category.create()
        cls.sample_service_record = ServiceRecord(
            parent_category=cls.sample_category,
            name="Информация о поставщике",
            datetime=datetime(2024, 9, 16, 3, 50),
        )
        cls.sample_service_record.create()
        cls.sample_record_level_2 = DataRecord(
            parent_category=cls.sample_category,
            alias="disclaimer",
            datetime=datetime(2024, 9, 16, 4,12),
        )
        cls.sample_record_level_2.create()
        cls.subcategory = CategoryRecord(
            parent_category=cls.sample_category,
            alias="rab001",
        )
        cls.subcategory.create()
        cls.sample_record_level_3 = DataRecord(
            parent_category=cls.subcategory,
            alias="rec001",
            datetime=datetime(2024, 9, 16, 3, 58),
        )
        cls.sample_record_level_3.create()

        cls.sample_records = {
            1: cls.sample_record_level_1,
            2: cls.sample_record_level_2,
            3: cls.sample_record_level_3,
        }

        cls.sample_categories = {
            0: cls.root_category_record,
            1: cls.sample_category,
            2: cls.subcategory,
        }

    def setUp(self):
        super().setUp()
        self.sample_project = TestLabjournalCache.sample_project

    def test_is_cache_singleton(self):
        """
        Tests that the LabjournalCache class is singleton
        """
        cache1 = LabjournalCache()
        cache2 = LabjournalCache()
        self.assertIs(cache1, cache2, "The LabjournalCache class is not singleton")
        self.assertIsNotNone(cache1, "The LabjournalCache class has not been created")

    @parameterized.expand([
        ('category', 0, "/"),
        ('category', 1, "/adult"),
        ('category', 2, "/adult/rab001"),
        ('data', 1, "/disclaimer"),
        ('data', 2, "/adult/disclaimer"),
        ('data', 3, "/adult/rab001/rec001")
    ])
    def test_path_no_service_record(self, record_type, record_index, expected_path):
        """
        Tests for the path in case when the record is not service

        :param record_type: 'data' for data record, 'category' for category record
        :param record_index: index of the data record to test
        :param expected_path: the path to be expected
        """
        sample_record = self._get_sample_record(record_type, record_index)
        t1 = time()
        path = sample_record.path
        t2 = time()
        self.assertEquals(path, expected_path, "The rabbit path has been badly evaluated")
        self.assertLess(t2-t1, 0.05, "The category path retrieval is too slow")

    def test_path_service_record(self):
        """
        Tests for the path in case when the category is service
        """
        with self.assertRaises(AttributeError, msg="Service record has no path"):
            print(self.sample_service_record.path)

    @parameterized.expand([
        ('category', 0, "/"),
        ('category', 1, "/adult"),
        ('category', 2, "/adult/rab001"),
        ('data', 1, "/disclaimer"),
        ('data', 2, "/adult/disclaimer"),
        ('data', 3, "/adult/rab001/rec001")
    ])
    def test_path_second_access(self, record_type, record_index, expected_path):
        """
        Tests whether the second access to the 'path' feature takes less time

        :param record_type: 'data' for data record, 'category' for category record
        :param record_index: index of the data record to test
        :param expected_path: the path to be expected
        """
        sample_record = self._get_sample_record(record_type, record_index)
        first_path = sample_record.path
        self.assertEquals(first_path, expected_path, "The rabbit path has been badly evaluated")
        with self.assertNumQueries(0):
            second_path = sample_record.path
        self.assertEquals(second_path, first_path, "The record path was damaged when passing through the cache")

    @parameterized.expand(path_category_change_provider())
    def test_path_parent_category_change(self, record_type, record_index, change_category_index, expected_path, flush):
        """
        Tests whether the cache is properly flushed when alias for the parent category changes

        :param record_type: 'data' for data record, 'category' for category record
        :param record_index: index of the data record to test
        :param change_category_index: index of the category to change
        :param expected_path: the resultant path to be expected
        :param flush: True if the labjournal cache must be flushed before the category change, false otherwise
        """
        record = self._get_sample_record(record_type, record_index)
        record.path
        self.sample_categories[2].path

        if flush:
            LabjournalCache().flush()

        category_to_change = self.sample_categories[change_category_index]
        old_category_alias = category_to_change.alias
        category_to_change.alias = 'new'
        category_to_change.update()

        self.assertEquals(record.path, expected_path, "No path is defined")

        category_to_change.alias = old_category_alias
        category_to_change.update()

    @parameterized.expand([
        ('category', 2, "/adult/rab001"),
        ('data', 2, "/adult/disclaimer"),
        ('data', 3, "/adult/rab001/rec001")
    ])
    def test_path_parent_category_flush(self, record_type, record_index, expected_path):
        """
        Tests whether the cache 2 is used when the cache 1 is flushed during the imitation of server restart

        :param record_type: 'data' for data record, 'category' for category record
        :param record_index: index of the data record to test
        :param expected_path: the path to be expected
        """
        record = self._get_sample_record(record_type, record_index)
        self.assertEquals(record.path, expected_path, "The record path is bad")
        LabjournalCache().flush()
        with self.assertNumQueries(1):
            self.assertEquals(record.path, expected_path, "The record path is bad")

    @parameterized.expand(find_by_path_provider())
    def test_find_by_path_positive(self, path, expected_record_type, expected_record_index):
        """
        Tests whether the record can be successfully found by its path

        :param path: the path to test
        :param expected_record_type: the record type the is expected to retrieve
        :param expected_record_index: index of a record that is expected to retrieve
        """
        record_set = RecordSet()
        t1 = time()
        actual_record = record_set.get((self.sample_project, path))
        t2 = time()
        expected_record = self._get_sample_record(expected_record_type, expected_record_index)
        self.assertRecordEqual(actual_record, expected_record)
        self.assertLessEqual(t2-t1, 0.5, "The category look by path is too slow")

    @parameterized.expand([
        ("/adult/rab001/rec002",),
        ("/adult/rab002/rec001",),
        ("/minor/rab001/rec001",),
        ("\\adult\\rab001\\rec001",),
        ('Русские буквы'),
        ("$adult$rab001%rec001"),
    ])
    def test_find_by_path_negative(self, path):
        """
        Tests that the method correctly processes invalid and non-existent paths

        :param path: an invalid or non-existent path
        """
        record_set = RecordSet()
        with self.assertRaises(EntityNotFoundException,
                               msg="Reference to non-existent paths must raise the EntityNotFoundException"):
            record_set.get((self.sample_project, path))

    @parameterized.expand(find_by_path_provider())
    def test_find_by_path_twice(self, path, expected_record_type, expected_record_index):
        """
        Ensures that finding by path doesn't depend on what time it happens to accomplish this action.

        :param path: the path to test
        :param expected_record_type: type of the record that is expected to find
        :param expected_record_index: index of the record that is expected to find
        """
        expected_record = self._get_sample_record(expected_record_type, expected_record_index)
        record_set = RecordSet()
        first_actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(first_actual_record, expected_record)
        with self.assertNumQueries(1):
            second_actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(second_actual_record, expected_record)

    @parameterized.expand(find_by_path_provider())
    def test_path_then_find_by_path(self, path, expected_record_type, expected_record_index):
        """
        Access to the path attribute and then ensures that the record can be successfully find by path

        :param path: the path to test
        :param expected_record_type: type of the record that is expected to find
        :param expected_record_index: index of the record that is expected to find
        """
        expected_record = self._get_sample_record(expected_record_type, expected_record_index)
        record_set = RecordSet()
        self.assertEquals(expected_record.path, path, "Record path discrepancy")
        with self.assertNumQueries(1):
            actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, expected_record)

    @parameterized.expand(find_by_path_provider())
    def test_find_by_path_then_path(self, path, expected_record_type, expected_record_index):
        """
        Finds the path attribute and then ensures that the record path can be successfully accesses

        :param path: the path to test
        :param expected_record_type: type of the record that is expected to find
        :param expected_record_index: index of the record that is expected to find
        """
        expected_record = self._get_sample_record(expected_record_type, expected_record_index)
        record_set = RecordSet()
        actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, expected_record)
        with self.assertNumQueries(0):
            self.assertEquals(actual_record.path, path, "Record path discrepancy")
            self.assertEquals(expected_record.path, path, "Record path discrepancy")

    @parameterized.expand(find_by_path_after_category_change())
    def test_find_by_path_change_and_find_by_path(self,
                                                  category_to_change_index,
                                                  path,
                                                  exception_to_throw,
                                                  expected_type,
                                                  expected_record_index,
                                                  flush
                                                  ):
        """
        Tests whether the cache properly flushes after the category change.
        The routine find some tested record, finds its parent category, changes the category itself and ensures
        that the "find by category" function still works properly

        :param category_to_change_index: index of the category you want to change
        :param path: path to the record that shall be found after that
        :exception_to_throw: an exception that shall be thrown during the record search or None if the record search
            shall be completed without any exceptions
        :param expected_type: type of record that is expected to find: 'data' or 'category'
        :param expected_record_index: index of the record that is expected to find
        :param flush: True to flush the cache 1 before making change to the category, False to don't do this
        """
        record_set = RecordSet()
        record_set.get((self.sample_project, "/adult/rab001/rec001"))
        record_set.get((self.sample_project, "/adult/rab001"))
        if flush:
            LabjournalCache().flush()
        category_to_change = self.sample_categories[category_to_change_index]
        category_to_change.alias = "new"
        category_to_change.update()
        if exception_to_throw is None:
            actual_record = record_set.get((self.sample_project, path))
            expected_record = self._get_sample_record(expected_type, expected_record_index)
            self.assertEquals(actual_record.id, expected_record.id, "Bad record has been found")
            self.assertEquals(actual_record.type, expected_record.type, "Record type mismatch")
        else:
            with self.assertRaises(exception_to_throw, msg="Exception to throw"):
                record_set.get((self.sample_project, path))

    @parameterized.expand([
        ("/", 'category', 0, 1),
        ("/adult", 'category', 1, 1),
        ("/adult/rab001", 'category', 2, 2),
        ("/disclaimer", 'data', 1, 1),
        ("/adult/disclaimer", 'data', 2, 2),
        ("/adult/rab001/rec001", 'data', 3, 2),
    ])
    def test_find_by_path_flush(self, path, expected_record_type, expected_record_index, expected_query_number):
        """
        Tests that the record can still be found by path after flushing cache 1 but not cache 2

        :param path: the path to test
        :param expected_record_type: type of the record that is expected to find
        :param expected_record_index: index of the record that is expected to find
        :param expected_query_number: expected number of queries that are required for
            the second retrieve of given record
        """
        expected_record = self._get_sample_record(expected_record_type, expected_record_index)
        record_set = RecordSet()
        actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, expected_record)
        LabjournalCache().flush()
        with self.assertNumQueries(expected_query_number):
            second_actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(second_actual_record, expected_record)

    def _get_sample_record(self, record_type, record_index):
        """
        Returns the data or category record that is suitable for particular test case

        :param record_type: 'data' for data record, 'category' for category record
        :param record_index: index of the data record to test
        :return: the record entity
        """
        if record_type == 'data':
            sample_record = self.sample_records[record_index]
        elif record_type == 'category':
            sample_record = self.sample_categories[record_index]
        else:
            raise ValueError("Unsupported record type")
        return sample_record

    def assertRecordEqual(self, actual_record, expected_record):
        """
        Asserts that two records are equal to each other

        :param actual_record: the first record to compare
        :param expected_record: the second record to compare
        """
        self.assertEqual(actual_record.id, expected_record.id, "The record ID is damaged")
        self.assertEqual(actual_record.project.id, expected_record.project.id,
                         "The related project is damaged")
        self.assertEqual(actual_record.level, expected_record.level, "The record level is damaged")
        self.assertEquals(actual_record.is_root_record, expected_record.is_root_record, "Rootness discrepancy")
        if not actual_record.is_root_record:
            self.assertEqual(actual_record.parent_category.id, expected_record.parent_category.id,
                             "The parent category is damaged")
            self.assertEqual(actual_record.alias, expected_record.alias, "The record alias is damaged")
            self.assertEqual(actual_record.datetime, expected_record.datetime, "The record datetime is damaged")
            self.assertEqual(actual_record.type, expected_record.type, "The record type is damaged")

    def tearDown(self):
        LabjournalCache().flush()
        super().tearDown()
