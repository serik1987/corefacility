from parameterized import parameterized

from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.labjournal_search_properties_set_object import LabjournalSearchPropertiesSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.user_set_object import UserSetObject
from ...entity.labjournal_record import RootCategoryRecord
from ...entity.labjournal_search_properties import SearchPropertiesSet
from ...exceptions.entity_exceptions import EntityNotFoundException
from ...models.enums import LabjournalRecordType


def positive_search_test_provider():
    return [
        (project, category, user,)
        for project in ('optical_imaging', 'the_rabbit_project')
        for category in ('root', 'a', 'b', 'sub')
        for user in ('leader', 'no_leader')
    ]


class TestLabjournalSearchPropertiesSet(BaseTestClass):
    """
    Provides test routines for the search properties
    """

    _user_set_object = None
    """ Container that contains all userful users """

    _group_set_object = None
    """ Container for all available groups """

    _project_set_object = None
    """ Container for all available projects """

    _record_set_object = None
    """ Container that contains all labjournal records """

    _search_properties_object = None
    """ Container that contains all search properties instances """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls._project_set_object = ProjectSetObject(cls._group_set_object)
        cls._record_set_object = RecordSetObject(cls._user_set_object, cls._project_set_object)
        cls._search_properties_object = \
            LabjournalSearchPropertiesSetObject(cls._user_set_object, cls._record_set_object)

    def setUp(self):
        super().setUp()
        self._container = TestLabjournalSearchPropertiesSet._search_properties_object.clone()
        self.initialize_filters()

    @parameterized.expand(positive_search_test_provider())
    def test_search_positive(self, project_cue, category_cue, user_cue):
        category, user = self._get_category_and_user(project_cue, category_cue, user_cue)
        self.apply_filter('category', category)
        self.apply_filter('user', user)
        self._test_object_iteration()

    @parameterized.expand(positive_search_test_provider())
    def test_search_count_positive(self, project_cue, category_cue, user_cue):
        category, user = self._get_category_and_user(project_cue, category_cue, user_cue)
        properties_set = SearchPropertiesSet()
        properties_set.category = category
        properties_set.user = user
        self.assertEquals(len(properties_set), 1, "Properties count mismatch")

    @parameterized.expand(positive_search_test_provider())
    def test_search_properties_pickup(self, project_cue, category_cue, user_cue):
        category, user = self._get_category_and_user(project_cue, category_cue, user_cue)
        properties_set = SearchPropertiesSet()
        properties_set.category = category
        properties_set.user = user
        self.apply_filter('category', category)
        self.apply_filter('user', user)
        property1 = properties_set[0]
        property2 = properties_set[0:10]
        property3 = properties_set.get(1234)
        property4 = self.container.entities[0]
        self.assertEntityFound(property1, property4, "Error in indexation")
        self.assertEntityFound(property2, property4, "Error in slicing")
        self.assertEntityFound(property3, property4, "Error in get() routine")
        with self.assertRaises(EntityNotFoundException):
            properties_set[1]
        with self.assertRaises(EntityNotFoundException):
            properties_set[-1]
        with self.assertRaises(EntityNotFoundException):
            properties_set[10:20]

    def test_bad_category(self):
        category = RootCategoryRecord(project=self.container.optical_imaging)
        category_list = category.children
        category_list.alias = 'd'
        category = category_list[0]
        user = self.container.active_users['optical_imaging']['leader']
        property_set = SearchPropertiesSet()
        property_set.category = category
        property_set.user = user
        for _ in property_set:
            self.fail("No search properties should be defined here.")
        self.assertEquals(len(property_set), 0, "No properties should be available here")
        with self.assertRaises(EntityNotFoundException):
            property_set[0]
        with self.assertRaises(EntityNotFoundException):
            property_set[0:10]
        with self.assertRaises(EntityNotFoundException):
            property_set.get(None)

    def test_search_properties_bad_user(self):
        category = RootCategoryRecord(project=self.container.optical_imaging)
        user = self._user_set_object[9]
        property_set = SearchPropertiesSet()
        property_set.category = category
        property_set.user = user
        for _ in property_set:
            self.fail("No search properties should be defined here.")
        self.assertEquals(len(property_set), 0, "No properties should be available here")
        with self.assertRaises(EntityNotFoundException):
            property_set[0]
        with self.assertRaises(EntityNotFoundException):
            property_set[0:10]
        with self.assertRaises(EntityNotFoundException):
            property_set.get(None)

    def test_no_category_specified(self):
        properties_set = SearchPropertiesSet()
        properties_set.category = RootCategoryRecord(project=self.container.the_rabbit_project)
        with self.assertRaises(RuntimeError):
            for _ in properties_set:
                self.fail("successful iteration when no filters were adjusted")
        with self.assertRaises(RuntimeError):
            len(properties_set)
        with self.assertRaises(RuntimeError):
            properties_set[0]
        with self.assertRaises(RuntimeError):
            properties_set[0:10]
        with self.assertRaises(RuntimeError):
            properties_set.get(None)

    def test_no_user_specified(self):
        properties_set = SearchPropertiesSet()
        properties_set.user = self.container.active_users['the_rabbit_project']['leader']
        with self.assertRaises(RuntimeError):
            for _ in properties_set:
                self.fail("successful iteration when no filters were adjusted")
        with self.assertRaises(RuntimeError):
            len(properties_set)
        with self.assertRaises(RuntimeError):
            properties_set[0]
        with self.assertRaises(RuntimeError):
            properties_set[0:10]
        with self.assertRaises(RuntimeError):
            properties_set.get(None)

    def test_syntax_sugar_positive(self):
        category = RootCategoryRecord(project=self.container.optical_imaging)
        search_properties = category.get_search_properties(self.container.active_users['optical_imaging']['leader'])
        self.apply_filter('category', category)
        self.apply_filter('user', self.container.active_users['optical_imaging']['leader'])
        self.assertEntityFound(search_properties, self.container[0], "Discrepancy in search properties")

    def test_syntax_sugar_no_root(self):
        category = RootCategoryRecord(project=self.container.optical_imaging)
        category_list = category.children
        category_list.alias = 'a'
        category = category_list[0]
        search_properties = category.get_search_properties(self.container.active_users['optical_imaging']['leader'])
        self.apply_filter('category', category)
        self.apply_filter('user', self.container.active_users['optical_imaging']['leader'])
        self.assertEntityFound(search_properties, self.container[0], "Discrepancy in search properties")

    def test_syntax_sugar_no_user(self):
        category = RootCategoryRecord(project=self.container.optical_imaging)
        category_list = category.children
        category_list.alias = 'a'
        category = category_list[0]
        search_properties = category.get_search_properties(self._user_set_object[9])
        self.assertIsNone(search_properties.id, "The entity must be creating")
        self.assertEquals(search_properties.state, 'creating')
        self.assertEquals(search_properties.category.id, category.id)
        self.assertEquals(search_properties.user.id, self._user_set_object[9].id)

    def test_syntax_sugar_no_category(self):
        category = RootCategoryRecord(project=self.container.optical_imaging)
        category_list = category.children
        category_list.alias = 'c'
        category = category_list[0]
        search_properties = category.get_search_properties(self.container.active_users['optical_imaging']['leader'])
        self.assertIsNone(search_properties.id, "The entity must be creating")
        self.assertEquals(search_properties.state, 'creating')
        self.assertEquals(search_properties.category.id, category.id)
        self.assertEquals(search_properties.user.id, self.container.active_users['optical_imaging']['leader'].id)

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
        self.assertEquals(actual_entity.properties, expected_entity.properties,
                          "%s: damage in the 'properties' field" % msg)

    def _get_category_and_user(self, project_cue, category_cue, user_cue):
        category = RootCategoryRecord(project=getattr(self.container, project_cue))
        if category_cue != 'root':
            category_list = category.children
            category_list.record_type = LabjournalRecordType.category
            if category_cue == 'sub':
                category_list.alias = 'a'
            else:
                category_list.alias = category_cue
            category = category_list[0]
            if category_cue == 'sub':
                category_list = category.children
                category_list.record_type = LabjournalRecordType.category
                category = category_list[0]
        user = self.container.active_users[project_cue][user_cue]
        return category, user


del BaseTestClass
