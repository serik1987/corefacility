import re
from collections import defaultdict
from datetime import datetime
from time import time

from django.test import TestCase
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.group import Group
from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import RecordHashtag
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor import NumberParameterDescriptor, \
    DiscreteParameterDescriptor, BooleanParameterDescriptor, StringParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RootCategoryRecord, DataRecord, \
    CategoryRecord, ServiceRecord, RecordSet
from ru.ihna.kozhukhov.core_application.entity.project import Project
from ru.ihna.kozhukhov.core_application.entity.user import User
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType, LabjournalFieldType
from ru.ihna.kozhukhov.core_application.utils import LabjournalCache

from ..data_providers.labjournal_cache_test_providers import *
from ...entity.labjournal_file import File


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

        chess_hashtag = RecordHashtag(
            description="chess",
            project=cls.sample_project,
        )
        chess_hashtag.create()

        seldom_hashtag = RecordHashtag(
            description="seldom",
            project=cls.sample_project,
        )
        seldom_hashtag.create()

        most_seldom_hashtag = RecordHashtag(
            description="most_seldom",
            project=cls.sample_project,
        )
        most_seldom_hashtag.create()

        record_types = [
            [],
            [LabjournalRecordType.data],
            [LabjournalRecordType.service],
            [LabjournalRecordType.category],
            [LabjournalRecordType.data, LabjournalRecordType.service],
            [LabjournalRecordType.data, LabjournalRecordType.category],
            [LabjournalRecordType.service, LabjournalRecordType.category],
            [LabjournalRecordType.data, LabjournalRecordType.service, LabjournalRecordType.category],
        ]

        cls.sample_category_descriptors = defaultdict(list)
        for sample_category_index, sample_category in cls.sample_categories.items():
            k = 0
            for l in range(12):
                sample_descriptor = NumberParameterDescriptor(
                    category=sample_category,
                    identifier="cat%d_param%d" % (sample_category_index, k),
                    description="Тестовый дескриптор (числовой)",
                    required=k % 7 == 0,
                    record_type=record_types[k % 8],
                    units="kg/am" if k % 5 == 0 else "amg",
                )
                if l != 0:
                    sample_descriptor.default = 3.48 * k
                sample_descriptor.create()
                cls.sample_category_descriptors[sample_category_index].append(sample_descriptor)
                k += 1
            for l in range(12):
                sample_descriptor = DiscreteParameterDescriptor(
                    category=sample_category,
                    identifier="cat%d_param%d" % (sample_category_index, k),
                    description="Тестовый дескриптор (дискретный)",
                    required=k % 7 == 0,
                    record_type=record_types[k % 8],
                )
                sample_descriptor.create()
                for m in range(5):
                    sample_descriptor.values.add(str(m), "Тестовое значение")
                if l != 0:
                    sample_descriptor.default = "3"
                    sample_descriptor.update()
                cls.sample_category_descriptors[sample_category_index].append(sample_descriptor)
                k += 1
            for l in range(12):
                sample_descriptor = BooleanParameterDescriptor(
                    category=sample_category,
                    identifier="cat%d_param%d" % (sample_category_index, k),
                    description="Тестовый дескриптор (булев)",
                    required=k % 7 == 0,
                    record_type= record_types[k % 8],
                )
                if l != 0:
                    sample_descriptor.default = k % 6 == 0
                sample_descriptor.create()
                cls.sample_category_descriptors[sample_category_index].append(sample_descriptor)
                k += 1
            for l in range(12):
                sample_descriptor = StringParameterDescriptor(
                    category=sample_category,
                    identifier="cat%d_param%d" % (sample_category_index, k),
                    description="Тестовый дескриптор (строковой)",
                    required=k % 7 == 0,
                    record_type= record_types[k % 8],
                )
                if l != 0:
                    sample_descriptor.default = str(k)
                sample_descriptor.create()
                cls.sample_category_descriptors[sample_category_index].append(sample_descriptor)
                k += 1
            for k, sample_descriptor in enumerate(cls.sample_category_descriptors[sample_category_index]):
                if k % 2 == 0:
                    sample_descriptor.hashtags.add([chess_hashtag.id])
                if k % 3 == 0:
                    sample_descriptor.hashtags.add([seldom_hashtag.id])
                if k % 4 == 0:
                    sample_descriptor.hashtags.add([most_seldom_hashtag.id])

        cls.expected_descriptors_for_record = {
            'data': {
                1: cls.sample_category_descriptors[0],
                2: [*cls.sample_category_descriptors[0], *cls.sample_category_descriptors[1]],
                3: [
                    *cls.sample_category_descriptors[0],
                    *cls.sample_category_descriptors[1],
                    *cls.sample_category_descriptors[2]
                ]
            },
            'category': {
                0: cls.sample_category_descriptors[0],
                1: [*cls.sample_category_descriptors[0], *cls.sample_category_descriptors[1]],
                2: [
                    *cls.sample_category_descriptors[0],
                    *cls.sample_category_descriptors[1],
                    *cls.sample_category_descriptors[2]
                ]
            }
        }

    def setUp(self):
        super().setUp()
        LabjournalCache().flush()

        self.sample_project = TestLabjournalCache.sample_project
        self.sample_category_descriptors = TestLabjournalCache.sample_category_descriptors
        self.expected_descriptors_for_record = TestLabjournalCache.expected_descriptors_for_record

    def test_is_cache_singleton(self):
        """
        Tests that the LabjournalCache class is singleton
        """
        cache1 = LabjournalCache()
        cache2 = LabjournalCache()
        self.assertIs(cache1, cache2, "The LabjournalCache class is not singleton")
        self.assertIsNotNone(cache1, "The LabjournalCache class has not been created")

    @parameterized.expand(general_data_with_path_provider())
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
        self.assertLessEqual(t2-t1, 1.0, "The category path retrieval is too slow")

    def test_path_service_record(self):
        """
        Tests for the path in case when the category is service
        """
        with self.assertRaises(AttributeError, msg="Service record has no path"):
            print(self.sample_service_record.path)

    @parameterized.expand(general_data_with_path_provider())
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

    @parameterized.expand([
        ("/", 'category', 0, 3),
        ("/adult", 'category', 1, 3),
        ("/adult/rab001", 'category', 2, 2),
        ("/disclaimer", 'data', 1, 3),
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

    @parameterized.expand(general_data_provider())
    def test_computed_descriptors_positive(self, record_type, record_index):
        """
        Tests that all descriptors are computed successfully.

        :param record_type: what record type to test: 'data' for data record and 'category' for category
        :param record_index: index of the testing record
        """
        sample_record = self._get_sample_record(record_type, record_index)
        t1 = time()
        actual_descriptors = sample_record.computed_descriptors
        t2 = time()
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)
        self.assertLessEqual(t2-t1, 1.0, "The descriptors computation process is too slow")

    def test_computed_descriptors_service_record(self):
        """
        Tests that all descriptors are retrieved as well for a service record
        """
        t1 = time()
        actual_descriptors = self.sample_service_record.computed_descriptors
        t2 = time()
        expected_descriptors = self.expected_descriptors_for_record['category'][1]
        # There must be defined exactly the same descriptors for a service record as for its parent category
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)
        self.assertLessEqual(t2-t1, 1.0, "The descriptor computation process is too slow")

    @parameterized.expand(general_data_provider())
    def test_computed_descriptors_twice(self, record_type, record_index):
        """
        Tests that the second descriptor computation doesn't require access to the database

        :param record_type: what record type to test: 'data' for data record and 'category' for category
        :param record_index: index of the testing record
        """
        sample_record = self._get_sample_record(record_type, record_index)
        first_actual_descriptors = sample_record.computed_descriptors
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        self.assertDescriptorListEqual(first_actual_descriptors, expected_descriptors)
        with self.assertNumQueries(0):
            second_actual_descriptors = sample_record.computed_descriptors
        self.assertDescriptorListEqual(second_actual_descriptors, expected_descriptors)

    def test_computed_descriptors_for_service_record_twice(self):
        """
        Tests that the second descriptor computation for service record doesn't require access to the database
        """
        first_actual_descriptors = self.sample_service_record.computed_descriptors
        expected_descriptors = self.expected_descriptors_for_record['category'][1]
        self.assertDescriptorListEqual(first_actual_descriptors, expected_descriptors)
        with self.assertNumQueries(0):
            second_actual_descriptors = self.sample_service_record.computed_descriptors
        self.assertDescriptorListEqual(second_actual_descriptors, expected_descriptors)

    @parameterized.expand(general_data_with_path_provider())
    def test_path_then_computed_descriptors(self, record_type, record_index, expected_path):
        """
        Tests that the cache data put after accessing to the 'path' property is still valid when we access to
        the 'computed_descriptors' property

        :param record_type: what type of record you would like to test: 'data' or 'category'
        :param record_index: index of a record to test index of the record to test
        :param expected_path: the path to be expected
        """
        sample_record = self._get_sample_record(record_type, record_index)
        self.assertEquals(sample_record.path, expected_path, "Record path mismatch")
        if record_type == 'data':
            with self.assertNumQueries(0):
                actual_descriptors = sample_record.computed_descriptors
        else:
            actual_descriptors = sample_record.computed_descriptors
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(find_by_path_provider())
    def test_find_by_path_then_computed_descriptors(self, path, expected_record_type, expected_record_index):
        """
        Tests that the descriptors can still be found when the cache data are put by the find by path feature

        :param path: path that will be used to find the records
        :param expected_record_type: record type that is expected to achieve after parsing the path
        :param expected_record_index: record index that is expected to achieve after parsing the path
        """
        expected_record = self._get_sample_record(expected_record_type, expected_record_index)
        expected_descriptors = self.expected_descriptors_for_record[expected_record_type][expected_record_index]
        record_set = RecordSet()
        actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, expected_record)
        if isinstance(actual_record, CategoryRecord):
            actual_descriptors = actual_record.computed_descriptors
        else:
            with self.assertNumQueries(0):
                actual_descriptors = actual_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(general_data_with_path_provider())
    def test_computed_descriptors_then_path(self, record_type, record_index, expected_path):
        """
        Tests whether the 'path' property can still be accessed after the 'computed_descriptors' property has been
        accessed.

        :param record_type: type of the record to test
        :param record_index: index of the record to test
        :param expected_path: the path to be expected
        """
        sample_record = self._get_sample_record(record_type, record_index)
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        actual_descriptors = sample_record.computed_descriptors
        if record_type == 'category':
            actual_path = sample_record.path
        else:
            with self.assertNumQueries(0):
                actual_path = sample_record.path
        self.assertEquals(actual_path, expected_path, "Record path mismatch")
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(general_data_with_path_provider())
    def test_computed_descriptors_then_find_by_path(self, record_type, record_index, path):
        """
        Tests whether the find_by_path' feature can still be accessed after the 'computed_descriptors' property
        has been accessed

        :param record_type: type of the record to test
        :param record_index: index of the record to test
        :param path: path to test
        """
        sample_record = self._get_sample_record(record_type, record_index)
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        actual_descriptors = sample_record.computed_descriptors
        record_set = RecordSet()
        if record_type == 'category':
            actual_record = record_set.get((self.sample_project, path))
        else:
            with self.assertNumQueries(1):
                actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, sample_record)
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(general_data_provider())
    def test_computed_descriptors_twice_with_flush(self, record_type, record_index):
        """
        Tests whether the 'computed_descriptors' property still works after flushing cache 1 but not cache 2

        :param record_type: type of the record
        :param record_index: index of the record
        """
        sample_record = self._get_sample_record(record_type, record_index)
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        actual_descriptors = sample_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)
        LabjournalCache().flush()
        if sample_record.is_root_record or sample_record.parent_category.is_root_record:
            second_actual_descriptors = sample_record.computed_descriptors
        else:
            with self.assertNumQueries(1):
                second_actual_descriptors = sample_record.computed_descriptors
        self.assertDescriptorListEqual(second_actual_descriptors, expected_descriptors)

    def test_computed_descriptors_for_service_record_twice_with_flush(self):
        """
        Tests whether the 'computed_descriptors' feature still works for service records after cache 1 has been flushed
        """
        expected_descriptors = self.expected_descriptors_for_record['data'][2]
        actual_descriptors = self.sample_service_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)
        LabjournalCache().flush()
        with self.assertNumQueries(1):
            actual_descriptors = self.sample_service_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(general_data_with_path_provider())
    def test_path_then_computed_descriptors_with_flush(self, record_type, record_index, expected_path):
        """
        Tests whether the 'computed_descriptors' still works when the 'path' property is extracted then
        cache 1 flushed

        :param record_type: type of the record
        :param record_index: index of the record
        :param expected_path: the path to be expected
        """
        sample_record = self._get_sample_record(record_type, record_index)
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        self.assertEquals(sample_record.path, expected_path, "Record path mismatch")
        LabjournalCache().flush()
        if record_type == 'category' or sample_record.parent_category.is_root_record:
            actual_descriptors = sample_record.computed_descriptors
        else:
            with self.assertNumQueries(1):
                actual_descriptors = sample_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(find_by_path_provider())
    def test_find_by_path_then_computed_descriptors_with_flush(self, path, expected_record_type, expected_record_index):
        """
        Tests whether the 'computed_descriptors' feature still works after 'path' property is used
        and cache 1 is flushed

        :param path: the path to test
        :param expected_record_type: record type that is expected to receive
        :param expected_record_index: record index that is expected to receive
        """
        expected_record = self._get_sample_record(expected_record_type, expected_record_index)
        expected_descriptors = self.expected_descriptors_for_record[expected_record_type][expected_record_index]
        record_set = RecordSet()
        actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, expected_record)
        LabjournalCache().flush()
        if actual_record.type == LabjournalRecordType.category or actual_record.parent_category.is_root_record:
            actual_descriptors = actual_record.computed_descriptors
        else:
            with self.assertNumQueries(1):
                actual_descriptors = actual_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(general_data_with_path_provider())
    def test_computed_descriptors_then_path_flushed(self, record_type, record_index, expected_path):
        """
        Tests whether the 'path' feature still works after 'computed_descriptors' application and cache flushing

        :param record_type: what record type you would like to test: 'category' or 'data'
        :param record_index: index of the record to test
        :param expected_path: the path that is expected to achieve by means of 'path' feature.
        """
        sample_record = self._get_sample_record(record_type, record_index)
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        self.assertEquals(sample_record.path, expected_path, "Record path mismatch")
        LabjournalCache().flush()
        if record_type == 'category' or sample_record.parent_category.is_root_record:
            actual_descriptors = sample_record.computed_descriptors
        else:
            with self.assertNumQueries(1):
                actual_descriptors = sample_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)

    @parameterized.expand(general_data_with_path_provider())
    def test_computed_descriptors_then_find_by_path_flushed(self, record_type, record_index, path):
        """
        Tests whether the 'find by path' feature still works after 'computed_descriptors' feature was applied then
        cache was flushed.

        :param record_type: what kind of record you would like to test: 'data' or 'category'
        :param record_index: number of record to test
        :param path: path of the selected record
        """
        sample_record = self._get_sample_record(record_type, record_index)
        expected_descriptors = self.expected_descriptors_for_record[record_type][record_index]
        actual_descriptors = sample_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)
        LabjournalCache().flush()
        record_set = RecordSet()
        if record_type == 'category' or sample_record.parent_category.is_root_record:
            actual_record = record_set.get((self.sample_project, path))
        else:
            with self.assertNumQueries(2):
                actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, sample_record)

    @parameterized.expand(custom_field_change_provider())
    def test_custom_field(self, identifier, value, expected_value, change_mode):
        """
        Tests whether custom field can be effectively assigned and revoked.

        :param identifier: identifier of the custom parameter
        :param value: which value to assign
        :param expected_value: which value shall be revoked
        :param change_mode: 'on_update to assign the value than reload the record; 'on_load' to reload the record
            then assign the value.
        """
        sample_record = self.sample_record_level_3
        if change_mode == 'on_update':
            setattr(sample_record, identifier, value)
            sample_record.update()
        record_set = RecordSet()
        sample_record = record_set.get(sample_record.id)
        if change_mode == 'on_load':
            setattr(sample_record, identifier, value)
        self.assertEquals(getattr(sample_record, identifier), expected_value,
                          "Failed to retrieve value of a custom parameter")
        self.assertIsNone(sample_record.custom_cat0_param5,
                          "Value of the custom parameter is expected to be none if the parameter is never assigned")

    def test_custom_field_bad_category(self):
        """
        Tests that the custom parameter is not accessible for the wrong category
        """
        sample_record = self.sample_record_level_2
        with self.assertRaises(AttributeError, msg="The custom parameter is still accessible from bad category"):
            print(sample_record.custom_cat2_param0)
        with self.assertRaises(AttributeError, msg="The custom parameter is still accessible from bad category"):
            print(sample_record.custom_cat2_param0)

    @parameterized.expand(custom_field_for_category_provider())
    def test_custom_field_for_category(self, category_index, name, value, expected_value, exception_to_throw):
        """
        Tests whether the custom parameters are properly set for categories as well

        :param category_index: index of a category to load
        :param name: name of the custom parameter to set
        :param value: the value to set
        :param expected_value: value the is expected to be recorded
        :param exception_to_throw: None if setting and updating the custom parameter is expected to be successful.
            When setting is expected to be failed, the argument should equal to a class of an exception that
            expected to be thrown.
        """
        sample_record = self.sample_categories[category_index]
        if exception_to_throw is not None:
            with self.assertRaises(exception_to_throw):
                setattr(sample_record, name, value)
            with self.assertRaises(exception_to_throw):
                print(getattr(sample_record, name))
        else:
            setattr(sample_record, name, value)
            self.assertEquals(getattr(sample_record, name), expected_value, "Assigned value mismatch")
            sample_record.update()
            record_set = RecordSet()
            sample_record = record_set.get(sample_record.id)
            self.assertEquals(getattr(sample_record, name), expected_value, "Assigned value mismatch")

    def test_custom_field_on_creating(self):
        """
        Tests that the custom field value can't be assigned when the entity is still creating
        """
        sample_record = DataRecord(
            parent_category=self.sample_category,
            alias="test",
            datetime=datetime(2024, 9, 21, 15, 23),
        )
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Custom parameter was set when the entity is in bad state"):
            sample_record.custom_cat0_param0 = 9.4
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Custom parameter was read when the entity is in bad state"):
            print(sample_record.custom_cat0_param0)

    def test_custom_field_on_deleted(self):
        """
        Tests that the custom field value can't be assigned or read when the entity has already been deleted.
        """
        record_set = RecordSet()
        sample_record = record_set.get(self.sample_record_level_3.id)
        sample_record.delete()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Custom parameter was set when the entity is in bad state"):
            sample_record.custom_cat0_param0 = 9.4
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Custom parameter was read when the entity is in bad state"):
            print(sample_record.custom_cat0_param0)

    def test_customparameters_field(self):
        """
        Tests that the 'customparameters' field works properly
        """
        sample_record = self.sample_record_level_3
        identifier_pattern = re.compile(r'^cat(\d+)_param(\d+)$')
        sample_values = dict()
        for identifier, descriptor in sample_record.computed_descriptors.items():
            identifier_match = identifier_pattern.match(identifier)
            cat = int(identifier_match[1])
            param = int(identifier_match[2])
            if descriptor.type == LabjournalFieldType.boolean:
                value = (cat * param) % 2 == 0
            elif descriptor.type == LabjournalFieldType.number:
                value = cat**param
            else:
                value = str(cat**param)
            sample_values[identifier] = value
            setattr(sample_record, 'custom_' + identifier, value)
        sample_record.update()
        self.assertEquals(sample_record.customparameters, sample_values,
                          "The 'customparameters' field is not correct")
        record_set = RecordSet()
        sample_record = record_set.get(sample_record.id)
        self.assertEquals(sample_record.customparameters, sample_values,
                          "The 'customparameters' field is not correct")

    @parameterized.expand([('custom_cat0_param12',), ('custom_cat0_param36',)])
    def test_custom_parameter_max_chars_exceed(self, name):
        """
        Tests what's happened if maximum number of characters in the custom parameter exceeded

        :param name: name of the custom parameter
        """
        sample_record = self.sample_record_level_3
        with self.assertRaises(EntityFieldInvalid, msg="Assigning more than 256 characters should be impossible"):
            setattr(sample_record, name, "="*257)

    @parameterized.expand(default_field_test_provider())
    def test_custom_parameter_default_value_positive(self,
                                                     name,
                                                     default_value,
                                                     category1_value,
                                                     category2_value,
                                                     record_type,
                                                     record_index,
                                                     expected_value,
                                                     ):
        """
        Tests the proper job of 'default_parameter_values' property

        :param name: name of custom parameter to test
        :param default_value: tests whether the default value of custom parameter was set or None if no value was set
        :param category1_value: tests whether the parameter was set for the level 1 category or None if no value was set
        :param category2_value: tests whether the parameter was set for the level 2 category or None if no value was set
        :param record_type: type of the record to test: 'data', 'category' or 'service'
        :param record_index: index of the record to test; useless for service records
        :param expected_value: the default value for the record that is expected
        """
        descriptor = None
        for current_descriptor in self.sample_category_descriptors[0]:
            if current_descriptor.identifier == name:
                descriptor = current_descriptor
                break
        else:
            self.fail("Malformed test: incorrect name of the custom parameter")
        record_set = RecordSet()
        if default_value is not None:
            descriptor = self.sample_categories[0].descriptors.get(descriptor.id)
            if descriptor.type == LabjournalFieldType.discrete:
                descriptor.values.add('grat', "Rectangular grating")
                descriptor.values.add('reti', "Retinotopical stimulus")
                descriptor.values.add('imag', "Natural images")
                descriptor.values.add('figu', "Geometrical figures")
            descriptor.default = default_value
            descriptor.update()
        if category1_value is not None:
            category = record_set.get(self.sample_categories[1].id)
            setattr(category, 'custom_%s' % name, category1_value)
            category.update()
        if category2_value is not None:
            category = record_set.get(self.sample_categories[2].id)
            setattr(category, 'custom_%s'% name, category2_value)
            category.update()
        if record_type == 'service':
            sample_record = self.sample_service_record
        else:
            sample_record = self._get_sample_record(record_type, record_index)
        LabjournalCache().clean_category(RootCategoryRecord(project=self.sample_project), None)
        t1 = time()
        actual_value = sample_record.default_values[name]
        t2 = time()
        self.assertEquals(actual_value, expected_value, "Bad value of the default value.")
        self.assertLessEqual(t2-t1, 1.0, "The default values computation process is too slow.")
        with self.assertNumQueries(0):
            second_actual_value = sample_record.default_values[name]
        self.assertEquals(second_actual_value, expected_value, "Bad value of the default value.")
        LabjournalCache().flush()
        if sample_record.is_root_record or sample_record.parent_category.is_root_record:
            third_actual_value = sample_record.default_values[name]
        else:
            with self.assertNumQueries(1):
                third_actual_value = sample_record.default_values[name]
        self.assertEquals(third_actual_value, expected_value, "Bad value of the default value.")

    @parameterized.expand(default_base_directory_provider())
    def test_base_path(self, root_basedir, category1_basedir, category2_basedir, category_index, expected_path):
        """
        Tests the 'base_path' field of the record

        :param root_basedir: the base directory for the root record or None if it should be remained to be unset
        :param category1_basedir: the base directory for the level 1 category or None if it should be remained to be
            unset
        :param category2_basedir: the base directory for the level 2 category or None if it should be remained to be
            unset
        :param category_index: index of a category to test
        :param expected_path: value of the 'base_path' field that is expected
        """
        self._prepare_for_base_directory_test(root_basedir, category1_basedir, category2_basedir)
        category = self.sample_categories[category_index]
        t1 = time()
        actual_path = category.base_path
        t2 = time()
        self.assertEquals(actual_path, expected_path, "Bad path revealed")
        self.assertLessEqual(t2-t1, 1.0, "The base path computation process is too slow")
        with self.assertNumQueries(0):
            actual_path = category.base_path
        self.assertEquals(actual_path, expected_path, "Bad path revealed")

    @parameterized.expand(categories_with_base_path_provider())
    def test_computed_descriptors_then_base_path(self, category_index, expected_base_path):
        self._prepare_for_base_directory_test()
        category = self.sample_categories[category_index]
        expected_descriptors = self.expected_descriptors_for_record['category'][category_index]
        actual_descriptors = category.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptors, expected_descriptors)
        with self.assertNumQueries(0):
            actual_base_path = category.base_path
        self.assertEquals(actual_base_path, expected_base_path, "Base path mismatch")

    @parameterized.expand(general_data_with_path_and_default_values_provider())
    def test_path_then_default_values(self, record_type, record_index, expected_path, expected_default_value):
        """
        Reads the path field, then default_value field

        :param record_type: the record type to consider: 'data', or 'category'
        :param record_index: index of the record within the record dataset
        :param expected_path: path to be expected
        :param expected_default_value: default value for cat0_param0 custom parameter
        """
        self._prepare_for_custom_parameter_test()
        sample_record = self._get_sample_record(record_type, record_index)
        self.assertEquals(sample_record.path, expected_path, "Record path mismatch")
        with self.assertNumQueries(0):
            actual_default_value = sample_record.default_values['cat0_param0']
        self.assertEquals(actual_default_value, expected_default_value, "Default value mismatch")

    @parameterized.expand(find_by_path_then_default_value_provider())
    def test_find_by_path_then_default_value(self,
                                             path,
                                             expected_record_type,
                                             expected_record_number,
                                             expected_default_value
                                             ):
        """
        Tests whether the system will work correctly if we find the record by path then read its default value

        :param path: the record path
        :param expected_record_type: type of the record we are expected to find: 'category' or 'data'
        :param expected_record_number: index of the record we are expected to find
        :param expected_default_value: expected default value of a custom parameter 'cat0_param0' of the record
        """
        expected_record = self._get_sample_record(expected_record_type, expected_record_number)
        self._prepare_for_custom_parameter_test()
        actual_record = RecordSet().get((self.sample_project, path))
        self.assertRecordEqual(actual_record, expected_record)
        with self.assertNumQueries(0):
            actual_default_value = actual_record.default_values['cat0_param0']
        self.assertEquals(actual_default_value, expected_default_value, "Default value mismatch")

    @parameterized.expand(data_records_with_default_values_provider())
    def test_computed_descriptors_then_default_values(self, record_index, expected_default_value):
        """
        Tests whether the system will work if we load all custom descriptors and then try to load default values

        :param record_index: index of the record to test
        :param expected_default_value: the default value to be expected
        """
        sample_record = self.sample_records[record_index]
        expected_descriptor_list = self.expected_descriptors_for_record['data'][record_index]
        self._prepare_for_custom_parameter_test()
        actual_descriptor_list = sample_record.computed_descriptors
        self.assertDescriptorListEqual(actual_descriptor_list, expected_descriptor_list, test_for_default=False)
        with self.assertNumQueries(0):
            actual_default_value = sample_record.default_values['cat0_param0']
        self.assertEquals(actual_default_value, expected_default_value, "Default values mismatch")

    @parameterized.expand(general_data_with_path_and_default_values_provider())
    def test_default_value_then_path(self, record_type, record_number, expected_path, expected_default_value):
        """
        Tests whether the system will work if we get the default value and then try to get the record path

        :param record_type: what kind of the record would you like to test: 'data' or 'category'?
        :param record_number: number of the record to test
        :param expected_path: the expected value for the record path
        :param expected_default_value: the expected default value of a custom parameter of the record
        """
        sample_record = self._get_sample_record(record_type, record_number)
        self._prepare_for_custom_parameter_test()
        actual_default_value = sample_record.default_values['cat0_param0']
        self.assertEquals(actual_default_value, expected_default_value, "Default value mismatch")
        with self.assertNumQueries(0):
            actual_path = sample_record.path
        self.assertEquals(actual_path, expected_path, "Record path mismatch")

    @parameterized.expand(general_data_with_path_and_default_values_provider())
    def test_default_value_then_find_by_path(self, record_type, record_number, path, expected_default_value):
        """
        tests whether the system will work if we get the default value then find the same record by path

        :param record_type: type of the record to test
        :param record_number: index of the record to test
        :param path: path to test the 'find by path' feature
        :param expected_default_value: default value of a 'cat0_param0' custom parameter that is expected to receive
        """
        sample_record = self._get_sample_record(record_type, record_number)
        self._prepare_for_custom_parameter_test()
        actual_default_value = sample_record.default_values['cat0_param0']
        self.assertEquals(actual_default_value, expected_default_value, "Default value mismatch")
        record_set = RecordSet()
        with self.assertNumQueries(1):
            actual_record = record_set.get((self.sample_project, path))
        self.assertRecordEqual(actual_record, sample_record)

    @parameterized.expand(categories_with_base_path_provider())
    def test_base_path_twice_with_flush(self, category_index, expected_base_path):
        """
        Tests whether the base path will work if we flush the record

        :param category_index: index of the category to test
        :param expected_base_path: record path to be expected
        """
        self._prepare_for_base_directory_test()
        sample_category = self.sample_categories[category_index]
        self.assertEquals(sample_category.base_path, expected_base_path, "Base path mismatch")
        LabjournalCache().flush()
        if sample_category.is_root_record:
            actual_base_path = sample_category.base_path
        else:
            with self.assertNumQueries(1):
                actual_base_path = sample_category.base_path
        self.assertEquals(actual_base_path, expected_base_path, "Base path mismatch")

    @parameterized.expand(file_path_provider())
    def test_full_file(self, record_index, expected_file_path):
        """
        Tests for the file path feature
        """
        self._prepare_for_base_directory_test()
        record = RecordSet().get(self.sample_records[record_index].id)
        file = File(
            record=record,
            name="neurons.dat",
        )
        self.assertEquals(file.path, expected_file_path, "File path mismatch")

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

    def assertDescriptorListEqual(self, actual_descriptors, expected_descriptors, test_for_default=True):
        """
        Asserts that two descriptor sets are identical to each other

        :param actual_descriptors: descriptor list that has been computed using a 'computed_descriptors' field
        :param expected_descriptors: desriptor list that is expected to see
        :param test_for_default: True to provide the default value test for each descriptor, False not to do this
        """
        expected_descriptors = list(expected_descriptors)
        for identifier, actual_descriptor in actual_descriptors.items():
            for descriptor_index, expected_descriptor in enumerate(expected_descriptors):
                if actual_descriptor.id == expected_descriptor.id:
                    break
            else:
                print(actual_descriptor)
                self.fail("Some extra descriptor were revealed during the descriptor computation")
            del expected_descriptors[descriptor_index]
            self.assertIsInstance(actual_descriptor, expected_descriptor.__class__, "Descriptor type mismatch")
            self.assertEquals(actual_descriptor.identifier, expected_descriptor.identifier,
                              "Descriptor identifier mismatch")
            self.assertEquals(identifier, expected_descriptor.identifier,
                              "The descriptor is present in cache under a bad key")
            self.assertEquals(actual_descriptor.index, expected_descriptor.index, "Descriptor index mismatch")
            self.assertEquals(actual_descriptor.description, expected_descriptor.description,
                              "Descriptor description mismatch")
            self.assertEquals(actual_descriptor.required, expected_descriptor.required,
                              "Descriptor requiredness mismatch")
            if test_for_default:
                self.assertEquals(actual_descriptor.default, expected_descriptor.default,
                              "Descriptor default value mismatch")
            self.assertEquals(set(actual_descriptor.record_type), set(expected_descriptor.record_type),
                              "Record type mismatch")
            if isinstance(actual_descriptor, NumberParameterDescriptor):
                self.assertEquals(actual_descriptor.units, expected_descriptor.units, "Descriptor units mismatch")
            if isinstance(actual_descriptor, DiscreteParameterDescriptor):
                actual_values = list(actual_descriptor.values)
                expected_values = list(expected_descriptor.values)
                sorted(actual_values, key=lambda value: value['id'])
                sorted(expected_values, key=lambda value: value['id'])
                self.assertEquals(actual_values, expected_values, "Available values mismatch")
            actual_hashtags = list(actual_descriptor.hashtags)
            expected_hashtags = list(expected_descriptor.hashtags)
            for hashtag in actual_hashtags:
                self.assertIsInstance(hashtag, RecordHashtag, "Bad class for the hashtag")
            sorted(actual_hashtags, key=lambda hashtag: hashtag.id)
            sorted(expected_hashtags, key=lambda hashtag: hashtag.id)
            for hashtag_index, actual_hashtag in enumerate(actual_hashtags):
                expected_hashtag = expected_hashtags[hashtag_index]
                self.assertEquals(actual_hashtag.id, expected_hashtag.id, "Hashtag ID mismatch")
        if len(expected_descriptors) > 0:
            print(expected_descriptors)
            self.fail("Some descriptors are missed during the descriptor computation")

    def _prepare_for_custom_parameter_test(self):
        """
        Properly sets values of cat0_param0 custom parameter for all subsequent categories
        """
        descriptor = self.sample_categories[0].descriptors.get('cat0_param0')
        descriptor.default = 0.0
        descriptor.update()

        record_set = RecordSet()
        sample_category = record_set.get(self.sample_categories[1].id)
        sample_category.custom_cat0_param0 = 2.0
        sample_category.update()

        sample_category = record_set.get(self.sample_categories[2].id)
        sample_category.custom_cat0_param0 = 3.0
        sample_category.update()

        LabjournalCache().clean_category(self.sample_categories[0])

    def _prepare_for_base_directory_test(self,
                                         root_basedir='white-rabbit',
                                         category1_basedir='adult',
                                         category2_basedir='rab1'
                                         ):
        """
        Properly sets base directories for all subsequent categories

        :param root_basedir: base directory for the root category
        :param category1_basedir: base directory for the category 1
        :param category2_basedir: base directory for the category 2
        """
        for loop_index, category_base_directory in enumerate((root_basedir, category1_basedir, category2_basedir)):
            if category_base_directory is None:
                continue
            if loop_index != 0:
                working_category = RecordSet().get(self.sample_categories[loop_index].id)
            else:
                working_category = RecordSet().get_root(self.sample_project)
            working_category.base_directory = category_base_directory
            working_category.update()

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
