from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_file import FileSet

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.labjournal_file_set_object import LabjournalFileSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.user_set_object import UserSetObject


def test_mode_provider():
    return [
        (BaseTestClass.TEST_ITERATION,),
        (BaseTestClass.TEST_COUNT,),
    ]

def record_filter_provider():
    return [
        (record_filter_index, test_mode)
        for record_filter_index in (1, 2, 5,)
        for (test_mode,) in test_mode_provider()
    ]


class TestLabjournalFileSet(BaseTestClass):
    """
    Provides test routines for the LabjournalFileSet
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user_set_object = UserSetObject()
        cls.group_set_object = GroupSetObject(cls.user_set_object)
        cls.project_set_object = ProjectSetObject(cls.group_set_object)
        cls.record_set_object = RecordSetObject(cls.user_set_object, cls.project_set_object)
        cls.file_set_object = LabjournalFileSetObject(cls.record_set_object)

    def setUp(self):
        self._container = TestLabjournalFileSet.file_set_object.clone()
        self.container.sort()
        self.initialize_filters()

    @parameterized.expand(test_mode_provider())
    def test_general_search(self, test_mode):
        """
        Tests search in general mode, i.e., if no filter settings were applied
        """
        self._test_all_access_features(test_mode, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand(record_filter_provider())
    def test_record_filter(self, filter_index, test_mode):
        """
        Tests the 'record' filter in the EntitySet
        """
        self.apply_filter('record', self.record_set_object[filter_index])
        self._test_all_access_features(test_mode, None, self.POSITIVE_TEST_CASE)

    def test_general_count(self):
        """
        Tests counting in general mode
        """
        file_set = FileSet()
        self.assertEquals(len(file_set), 1344, "Bad number of files in the file set")

    @parameterized.expand([(1,), (2,), (5,),])
    def test_record_filter_count(self, record_filter_index):
        """
        Tests counting when the record filter is adjusted
        """
        record = self.record_set_object[record_filter_index]
        file_set = FileSet()
        file_set.record = record
        self.assertEquals(len(file_set), 3, "Bad number of files in a single record")


del BaseTestClass
