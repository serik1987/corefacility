from time import time
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType, LabjournalRecordType
from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import HashtagSet

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_hashtag_set_object import RecordHashtagSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.user_set_object import UserSetObject
from ..data_providers.entity_sets import filter_data_provider
from ...entity.labjournal_record import RecordSet


def search_mode_provider():
    return [(BaseTestClass.TEST_ITERATION,), (BaseTestClass.TEST_COUNT,),]

def general_search_provider():
    return filter_data_provider(
        [
            ('optical_imaging', LabjournalHashtagType.record),
            ('the_rabbit_project', LabjournalHashtagType.record),
            ('extra_project', LabjournalHashtagType.record),
            ('optical_imaging', LabjournalHashtagType.file),
        ],
        search_mode_provider(),
    )

def description_filter_provider():
    return filter_data_provider(
        [
            "",
            "р",
            "ш",
            "x",
            "ред",
            "шах",
            "xxx",
            "редк",
            "редч",
            "xxxx",
            "редкий",
            "редчайший",
            "шахматный",
            "fkuhgkjfdhgkjfd",
            "ый",
            "ий",
            "чайш",
            "атн",
        ],
        search_mode_provider()
    )

def hashtag_filter_provider():
    filter_data = [
        (RecordSet.LogicType.AND, ["редкий"], 139),
        (RecordSet.LogicType.AND, ["шахматный", "редчайший"], 104),
        (RecordSet.LogicType.AND, [], 896),
        (RecordSet.LogicType.AND, ["шахматный", "редкий"], 70),
        (RecordSet.LogicType.AND, ["редкий", "редчайший"], 35),
        (RecordSet.LogicType.AND, ["шахматный", "редкий", "редчайший"], 35),
        (RecordSet.LogicType.OR, ["редкий"], 139),
        (RecordSet.LogicType.OR, ["шахматный"], 208),
        (RecordSet.LogicType.OR, [], 896),
        (RecordSet.LogicType.OR, ["шахматный", "редкий"], 277),
        (RecordSet.LogicType.OR, ["редкий", "редчайший"], 208),
        (RecordSet.LogicType.OR, ["шахматный", "редкий", "редчайший"], 277),
    ]
    return filter_data


class TestRecordHashtagSet(BaseTestClass):
    """
    Tests the searching facilities for the HashtagSet
    """

    _user_set_object = None
    """ User list that is used for testing purpose """

    _group_set_object = None
    """ Group list that is used for testing purpose """

    _project_set_object = None
    """ Projects that are used for testing purpose """

    _record_set_object = None
    """ Records that are used for testing purpose """

    _record_hashtag_set_object = None
    """ Hashtags that are used for testing purpose """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls._project_set_object = ProjectSetObject(cls._group_set_object)
        cls._record_set_object = RecordSetObject(cls._user_set_object, cls._project_set_object)
        cls._record_hashtag_set_object = RecordHashtagSetObject(cls._record_set_object)

    def setUp(self):
        super().setUp()
        self._container = TestRecordHashtagSet._record_hashtag_set_object.clone()
        self._container.sort()
        self.initialize_filters()

    @parameterized.expand(general_search_provider())
    def test_general_search(self, project_cue, hashtag_type, test_mode):
        """
        Tests the general search facilities

        :param project_cue: cue for the considering project
        :param hashtag_type: A value for the hashtag filter
        :param test_mode: either ITERATION or COUNT
        """
        if project_cue == 'extra_project':
            project = self._project_set_object.get_by_alias('nsw')
        else:
            project = getattr(self._record_set_object, project_cue)
        self.apply_filter('project', project)
        self.apply_filter('type', hashtag_type)
        self._test_all_access_features(test_mode, None, self.POSITIVE_TEST_CASE)

    def test_no_type_filter(self):
        """
        Tests that the type filter is required
        """
        hashtag_set = HashtagSet()
        hashtag_set.project = self._record_set_object.optical_imaging
        with self.assertRaises(RuntimeError, msg="the HashtagSet should not work without the type filter"):
            for _ in hashtag_set:
                self.fail("the HashtagSet should not work without the type filter")

    def test_no_project_filter(self):
        """
        Tests that the project filter is required
        """
        hashtag_set = HashtagSet()
        hashtag_set.type = LabjournalHashtagType.record
        with self.assertRaises(RuntimeError, msg="the HashtagSet should not work without the project filter"):
            for _ in hashtag_set:
                self.fail("the HashtagSet should not work without the project filter")

    @parameterized.expand(description_filter_provider())
    def test_description_filter(self, search_string, test_mode):
        """
        Tests the 'description' filter

        :param search_string: a query string to search
        :param search_mode: iteration or count
        """
        self.apply_filter('project', self._record_set_object.optical_imaging)
        self.apply_filter('type', LabjournalHashtagType.record)
        self.apply_filter('description', search_string)
        self._test_all_access_features(test_mode, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand(hashtag_filter_provider())
    def test_hashtag_filter_count(self, filter_logic, filter_value, expected_counts):
        """
        Tests whether the hashtag filter successfully works on counting the records

        :param filter_logic: the logic to apply
        :param filter_value: value of the hashtag filter
        :param expected_counts: expected  number of counts
        """
        self.container.filter_by_project(self._record_set_object.optical_imaging)
        filter_value = [self.container.get_by_alias(description) for description in filter_value]
        record_set = RecordSet()
        record_set.hashtag_logic = filter_logic
        record_set.hashtags = filter_value
        self.assertEquals(len(record_set), expected_counts, "General counts mismatch")

    @parameterized.expand(hashtag_filter_provider())
    def test_hashtag_filter_iteration(self, filter_logic, filter_value, expected_counts):
        """
        Tests whether the hashtag filter successfully works on iterating the records

        :param filter_logic: the logic to apply
        :param filter_value: value of the hashtag filter
        :param expected_counts: expected  number of counts
        """
        self.container.filter_by_project(self._record_set_object.optical_imaging)
        print_filter_value = list(filter_value)
        filter_value = [self.container.get_by_alias(description) for description in filter_value]
        record_set = RecordSet()
        record_set.hashtag_logic = filter_logic
        record_set.hashtags = filter_value
        t1 = time()
        actual_records = list(record_set)
        t2 = time()
        self.assertEquals(len(actual_records), expected_counts,
                          "Discrepancy between the actual records retrieved and the expected counts")
        self.assertLessEqual(t2-t1, 50 * len(actual_records), "The filtration process is too slow")

        def expected_record_filter_function(record):
            actual_hashtags = [hashtag.id for hashtag in record.hashtags]
            expected_hashtags = [hashtag.id for hashtag in filter_value]
            if len(filter_value) == 0:
                result = True
            elif filter_logic == RecordSet.LogicType.AND:
                result = True
                for expected_hashtag in expected_hashtags:
                    if expected_hashtag not in actual_hashtags:
                        result = False
                        break
            elif filter_logic == RecordSet.LogicType.OR:
                result = False
                for expected_hashtag in expected_hashtags:
                    if expected_hashtag in actual_hashtags:
                        result = True
                        break
            else:
                raise ValueError("Bad hashtag logic")
            return result
        expected_records = list(self._record_set_object.entities)
        expected_records = list(filter(expected_record_filter_function, expected_records))
        expected_record_ids = {record.id for record in expected_records}
        self.assertEquals(len(expected_records), expected_counts, "The test-case is bad-conditioned")

        actual_records_considered = set()
        for actual_record in record_set:
            self.assertNotIn(actual_record.id, actual_records_considered,
                             "The record with ID=%d has been retrieved twice" % actual_record.id)
            self.assertIn(actual_record.id, expected_record_ids,
                          "The record with ID=%d has been retrieved but is not expected to pass the filter" %
                          actual_record.id)
            expected_record = None
            for current_record in expected_records:
                if actual_record.id == current_record.id:
                    expected_record = current_record
                    break
            self.assertEquals(actual_record.parent_category.id, expected_record.parent_category.id,
                              "Parent category mismatch")
            self.assertEquals(actual_record.project.id, expected_record.project.id, "Related project mismatch")
            self.assertEquals(actual_record.level, expected_record.level, "Record level mismatch")
            if actual_record.type != LabjournalRecordType.service:
                self.assertEquals(actual_record.alias, expected_record.alias, "Record alias mismatch")
            else:
                self.assertEquals(actual_record.name, expected_record.name, "Record name mismatch")
            self.assertEquals(actual_record.type, expected_record.type, "Record type mismatch")
            self.assertIsInstance(actual_record, expected_record.__class__, "Bad record type")
            self.assertEquals(actual_record.comments, expected_record.comments, "Record comments mismatch")
            actual_hashtags = {hashtag.description for hashtag in actual_record.hashtags}
            expected_hashtags = {hashtag.description for hashtag in expected_record.hashtags}
            self.assertEquals(actual_hashtags, expected_hashtags, "Record hashtag mismatch")
            actual_records_considered.add(actual_record.id)
            expected_record_ids.remove(actual_record.id)

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        """
        Asserts that the entity has been successfully found.
        Class derivatives can re-implement this method to ensure that all entity fields were uploaded successfully.

        :param actual_entity: the entity found in the database
        :param expected_entity: the entity expected to be found in the database
        :param msg: message to print when the entity is failed to be found
        :return: nothing
        """
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.description, expected_entity.description,
                          "%s: Hashtag description mismatch" % msg)


del BaseTestClass
