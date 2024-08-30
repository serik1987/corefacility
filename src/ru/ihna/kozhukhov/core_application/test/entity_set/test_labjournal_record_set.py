from datetime import datetime

from parameterized import parameterized

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.user_set_object import UserSetObject
from ...entity.labjournal_record.complex_interval import ComplexInterval
from ...entity.labjournal_record.record_set import RecordSet
from ...entity.labjournal_record.root_category_record import RootCategoryRecord
from ...models.enums.labjournal_record_type import LabjournalRecordType


class TestLabjournalRecordSet(BaseTestClass):
    """
    Tests sets of the laboratory journal records
    """

    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _record_set_object = None

    @classmethod
    def setUpTestData(cls):
        """
        Sets up the test data
        """
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls._project_set_object = ProjectSetObject(cls._group_set_object)
        cls._record_set_object = RecordSetObject(cls._user_set_object, cls._project_set_object)

    def setUp(self):
        self._container = TestLabjournalRecordSet._record_set_object.clone()
        self.container.sort()
        self.initialize_filters()

    def test_all_access_features(self):
        record_set = RecordSet()
        self.assertEquals(len(record_set), len(self.container), "Mismatch in number of items in the list")
        for record in record_set:
            matches = list(filter(lambda another_record: another_record.id == record.id, self.container.entities))
            if len(matches) != 1:
                self.fail("No matching entries for the record %s" % repr(record))

    @parameterized.expand([
        (BaseTestClass.TEST_ITERATION,),
        (BaseTestClass.TEST_COUNT,)
    ])
    def test_parent_category_filter(self, test_mode):
        self._apply_parent_category()
        self._test_all_access_features(test_mode, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand([
        (ComplexInterval(-float('inf'), -float('inf')),),
        (ComplexInterval(-float('inf'), float('inf')),),
        (ComplexInterval(datetime(2024, 1, 1, 12, 0, 0), float('inf')),),
        (ComplexInterval(
            datetime(2024, 1, 1, 12, 0, 0),
            datetime(2024, 1, 1, 12, 0, 0)
        ), ),
        (ComplexInterval(-float('inf'), datetime(2024, 1, 1, 12, 0)), ),
        (ComplexInterval(
            datetime(2024, 1, 1, 8, 0),
            datetime(2024, 1, 1, 16, 0)), ),
        (ComplexInterval(
            datetime(2024, 1, 1, 6, 0),
            datetime(2024, 1, 1, 12, 0),
        ) | ComplexInterval(
            datetime(2024, 1, 1, 18, 0),
            float('inf')
        ), ),
        (ComplexInterval(
            -float('inf'),
            datetime(2024, 1, 1, 6, 0),
        ) | ComplexInterval(
            datetime(2024, 1, 1, 12, 0),
            datetime(2024, 1, 1, 18, 0),
        ), ),
    ])
    def test_datetime_filter(self, time):
        """
        Tests the absolute datetime filter by means of 0 points
        """
        self._apply_parent_category()
        self.apply_filter('datetime', time)
        self._test_all_access_features(self.TEST_COUNT, None, self.POSITIVE_TEST_CASE)
        self._test_all_access_features(self.TEST_ITERATION, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand([
        ([LabjournalRecordType.category, LabjournalRecordType.service, LabjournalRecordType.data], ),
        ([LabjournalRecordType.category, LabjournalRecordType.service], ),
        ([LabjournalRecordType.category, LabjournalRecordType.data], ),
        ([LabjournalRecordType.service, LabjournalRecordType.data], ),
        ([LabjournalRecordType.category], ),
        ([LabjournalRecordType.service], ),
        ([LabjournalRecordType.data], ),
        ([], ),
    ])
    def test_types_filter(self, types):
        """
        Tests the 'types' filter

        :param types: selects only records belonging to a given types
        """
        self._apply_parent_category()
        self.apply_filter('types', types)
        self._test_all_access_features(self.TEST_COUNT, None, self.POSITIVE_TEST_CASE)
        self._test_all_access_features(self.TEST_ITERATION, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand([
        ("С",),
        ("Служеб"),
        ("Служб",),
        ("Служебная запись 1"),
    ])
    def test_name_filter(self, name):
        self._apply_parent_category()
        self.apply_filter('name', name)
        self._test_all_access_features(self.TEST_COUNT, None, self.POSITIVE_TEST_CASE)
        self._test_all_access_features(self.TEST_ITERATION, None, self.POSITIVE_TEST_CASE)

    def _apply_parent_category(self):
        record_set = RootCategoryRecord(project=self.container.optical_imaging).children
        record_set.alias = 'a'
        record = record_set[0]
        self.apply_filter('parent_category', record)


del BaseTestClass
