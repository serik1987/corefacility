from parameterized import parameterized

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.parameter_descriptor_set_object import ParameterDescriptorSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.viewed_parameter_set_object import ViewedParameterSetObject
from ...entity.labjournal_record import RootCategoryRecord
from ...models.enums import LabjournalRecordType


def positive_test_case_provider():
    projects = ['optical_imaging', 'the_rabbit_project']
    categories = ['root', 'a', 'b', 'sub']
    users = ['leader', 'no_leader']
    modes = [BaseTestClass.TEST_ITERATION, BaseTestClass.TEST_COUNT]
    return [
        (project, category, user, mode)
        for project in projects
        for category in categories
        for user in users
        for mode in modes
    ]


def light_test_provider():
    return [BaseTestClass.TEST_ITERATION, BaseTestClass.TEST_COUNT]


class TestViewedParameterSet(BaseTestClass):
    """
    Tests the viewed parameter sets
    """

    _user_set_object = None
    """ Container for all tested users """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls._project_set_object = ProjectSetObject(cls._group_set_object)
        cls._record_set_object = RecordSetObject(cls._user_set_object, cls._project_set_object)
        cls._parameter_descriptor_set_object = ParameterDescriptorSetObject(cls._record_set_object)
        cls._viewed_parameter_set_object = ViewedParameterSetObject(
            cls._user_set_object,
            cls._record_set_object,
            cls._parameter_descriptor_set_object,
        )

    def setUp(self):
        super().setUp()
        self._container = TestViewedParameterSet._viewed_parameter_set_object.clone()
        self.container.sort()
        self.initialize_filters()

    @parameterized.expand(positive_test_case_provider())
    def test_positive_cases(self, project, category, user, mode):
        """
        Provides positive test cases for the viewed parameters list

        :param project: project cue to use for testing
        :param category: category cue to use for testing
        :param user: user cue to use for testing
        :param mode: ITERATION to test iterations, COUNT to test counting
        """
        project_alias = project
        project = getattr(self._record_set_object, project)
        root_category = RootCategoryRecord(project=project)
        if category == 'root':
            category = root_category
        else:
            child_categories = root_category.children
            child_categories.type = LabjournalRecordType.category
            if category == 'b':
                child_categories.alias = 'b'
                category = child_categories[0]
            else:
                child_categories.alias = 'a'
                child_category = child_categories[0]
                if category == 'a':
                    category = child_category
                else:
                    child_categories = child_category.children
                    child_categories.type = LabjournalRecordType.category
                    category = child_categories[0]
        user = self._viewed_parameter_set_object.active_users[project_alias][user]
        self.apply_filter('category', category)
        self.apply_filter('user', user)
        self._test_all_access_features(mode, None, self.POSITIVE_TEST_CASE)

    @parameterized.expand(light_test_provider())
    def test_no_user(self, mode):
        """
        Tests an exceptional case when no user context was set

        :param mode: either ITERATION or COUNT
        """
        project = self._record_set_object.optical_imaging
        category = RootCategoryRecord(project=project)
        self.apply_filter('category', category)
        with self.assertRaises(RuntimeError, msg="The ViewedParameterSet must not work without user context"):
            self._test_all_access_features(mode, 0, self.POSITIVE_TEST_CASE)

    @parameterized.expand(light_test_provider())
    def test_no_category(self, mode):
        """
        Tests an exceptional case when no category context was set

        :param mode: either ITERATION or COUNT
        """
        user = self._viewed_parameter_set_object.active_users['optical_imaging']['leader']
        self.apply_filter('user', user)
        with self.assertRaises(RuntimeError, msg="The ViewedParameterSet must not work without category context"):
            self._test_all_access_features(mode, 0, self.POSITIVE_TEST_CASE)


del BaseTestClass
