from time import time
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.parameter_descriptor_set import \
    ParameterDescriptorSet
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.string_parameter_descriptor import \
    StringParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record import \
    RootCategoryRecord
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType

from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.parameter_descriptor_set_object import ParameterDescriptorSetObject


def category_filter_provider():
    all_categories = [
        ['optical_imaging'],
        ['optical_imaging', 'a'],
        ['optical_imaging', 'a', 'subcat'],
        ['optical_imaging', 'b'],
        ['optical_imaging', 'b', 'subcat'],
        ['optical_imaging', 'c'],
        ['the_rabbit_project'],
        ['the_rabbit_project', 'a'],
        ['the_rabbit_project', 'a', 'subcat'],
        ['the_rabbit_project', 'b'],
        ['the_rabbit_project', 'b', 'subcat'],
        ['the_rabbit_project', 'c'],
    ]
    test_modes = [
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]
    return [
        (category, *mode_details,)
        for category in all_categories
        for mode_details in test_modes
    ]

def descriptor_swap_provider():
    descriptor_index_list = [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 0),
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),
        (3, 0),
        (3, 1),
        (3, 2),
        (3, 3),
    ]
    return [
        (category_cue, *descriptor_indices)
        for category_cue in (True, False)
        for descriptor_indices in descriptor_index_list
    ]


class TestParameterDescriptorSet(BaseTestClass):
    """
    Provides test routines for the parameter descriptor set
    """

    _user_set_object = None
    """ Defines the list of users to deal with """

    _group_set_object = None
    """ Defines the list of groups to deal with """

    _project_set_object = None
    """ Defines the list of all projects to deal with """

    _record_set_object = None
    """ Defines list of all records to deal with """

    _parameter_descriptor_set_object = None
    """ Defines list of all parameter descriptors to set """

    _default_category = None
    """ The default category to use """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls._project_set_object = ProjectSetObject(cls._group_set_object)
        cls._record_set_object = RecordSetObject(cls._user_set_object, cls._project_set_object)
        cls._parameter_descriptor_set_object = ParameterDescriptorSetObject(cls._record_set_object)

    def setUp(self):
        self._container = TestParameterDescriptorSet._parameter_descriptor_set_object.clone()
        self.initialize_filters()
        self._default_category = RootCategoryRecord(project=self._record_set_object.optical_imaging)
        category_set = self._default_category.children
        category_set.alias = 'a'
        self._default_category = category_set[0]

    def test_general_search(self):
        """
        Tests that the general search (without specification of the category) is not possible
        """
        general_set = ParameterDescriptorSet()
        with self.assertRaises(RuntimeError, msg="The general search is unsafe and must be inavailable"):
            for descriptor in general_set:
                print(repr(descriptor))

    @parameterized.expand(category_filter_provider())
    def test_category_filter(self, category_path, feature_index, arg, test_type):
        """
        Provides a category filter to test

        :param category_path: full path to the category to test
        :param feature_index: see _test_all_access_features
        :param arg: see _test_all_access_features
        :param test_type: see _test_all_access_features
        """
        category = None
        for category_path_item in category_path:
            if category is None:
                category = RootCategoryRecord(project=getattr(self._record_set_object, category_path_item))
            else:
                record_set = category.children
                record_set.alias = category_path_item
                category = record_set[0]
        self.apply_filter('category', category)
        self._test_all_access_features(feature_index, arg, test_type)

    def test_is_parked_default(self):
        """
        Tests that the entities are not parked by default
        """
        parameter_set = ParameterDescriptorSet()
        with self.assertRaises(RuntimeError, msg="The function is not available in general case"):
            parameter_set.is_parked

    @parameterized.expand([(True,), (False,),])
    def test_is_parked_not_parked(self, is_root):
        """
        Tests value of the is_parked property by default, i.e., when no parking is applied

        :param is_root: True if the category is root
        """
        category = self._load_category(is_root)
        self.assertFalse(category.descriptors.is_parked, "By default, the descriptor list is not parked")

    @parameterized.expand([(True,), (False,),])
    def test_park(self, is_root):
        """
        Tests the park() method

        :param is_root: True if the category is root
        """
        category = self._load_category(is_root)
        category.descriptors.park()
        self.assertTrue(category.descriptors.is_parked, "The descriptor list is parked after the park")

    @parameterized.expand([(True,), (False,),])
    def test_descriptor_add(self, is_root):
        """
        Tests that after the category add: (a) the system is not parked; (b) the added item is placed at the bottom
        """
        category = self._load_category(is_root)
        descriptor_sequence = [descriptor.id for descriptor in category.descriptors]
        category.descriptors.park()
        another_descriptor = StringParameterDescriptor(
            category=category,
            identifier="sample_identifier",
            description="Sample Identifier",
            required=True,
            record_type=[LabjournalRecordType.service,],
        )
        another_descriptor.create()
        descriptor_sequence.append(another_descriptor.id)
        self.assertFalse(category.descriptors.is_parked, "The descriptor list is not parked after the category add")
        index = 0
        for descriptor in category.descriptors:
            self.assertEquals(descriptor.id, descriptor_sequence[index],
                              "The descriptor order was lost in this test case")
            index += 1

    @parameterized.expand([(True,), (False,),])
    def test_descriptor_after_add(self, is_root):
        """
        Test whether the descriptor parking losts the descriptor order

        :param is_root: True to test the root category, False otherwise
        """
        category = self._load_category(is_root)
        descriptor_sequence = [descriptor.id for descriptor in category.descriptors]
        category.descriptors.park()
        another_descriptor = StringParameterDescriptor(
            category=category,
            identifier="sample_identifier",
            description="Sample Identifier",
            required=True,
            record_type=[LabjournalRecordType.service, ],
        )
        another_descriptor.create()
        descriptor_sequence.append(another_descriptor.id)
        category.descriptors.park()
        self.assertTrue(category.descriptors.is_parked, "The descriptor list must be parked after parking")
        index = 0
        for descriptor in category.descriptors:
            self.assertEquals(descriptor.id, descriptor_sequence[index],
                              "The descriptor order was lost during the parking")
            index += 1

    @parameterized.expand([
        (0, True, False,),
        (0, False, False,),
        (1, True, False,),
        (1, False, False,),
        (2, True, False,),
        (2, False, False,),
        (3, True, True,),
        (3, False, True,),
    ])
    def test_descriptor_remove(self, removal_index, is_root, is_parked_expected):
        """
        Tests whether the descriptor sequence is not parked after the descriptor remove

        :param removal_index: index of the element to remove
        :param is_root: True to test the root category, False otherwise
        :param is_parked_expected: True if items are expected to be parked after removal, False otherwise
        """
        category = self._load_category(is_root)
        self.apply_filter('category', category)
        descriptor_sequence = [descriptor.id for descriptor in category.descriptors]
        category.descriptors.park()
        removing_descriptor = self.container.entities[removal_index]
        removing_descriptor = category.descriptors.get(removing_descriptor.id)
        descriptor_sequence.remove(removing_descriptor.id)
        removing_descriptor.delete()
        self.assertEquals(category.descriptors.is_parked, is_parked_expected,
                          "The descriptor set must be non-parked after the descriptor remove")
        index = 0
        for descriptor in category.descriptors:
            self.assertEquals(descriptor.id, descriptor_sequence[index],
                              "The descriptor ordering was lost during the element removal")
            index += 1

    @parameterized.expand([
        (0, True,),
        (0, False,),
        (1, True,),
        (1, False,),
        (2, True,),
        (2, False,),
        (3, True,),
        (3, False,),
    ])
    def test_descriptor_after_remove(self, removal_index, is_root):
        """
        Tests whether the descriptor sequence is not parked after the descriptor remove

        :param removal_index: index of the element to remove
        :param is_root: True to test the root category, False otherwise
        """
        category = self._load_category(is_root)
        self.apply_filter('category', category)
        descriptor_sequence = [descriptor.id for descriptor in category.descriptors]
        category.descriptors.park()
        removing_descriptor = self.container.entities[removal_index]
        removing_descriptor = category.descriptors.get(removing_descriptor.id)
        descriptor_sequence.remove(removing_descriptor.id)
        removing_descriptor.delete()
        category.descriptors.park()
        index = 0
        for descriptor in category.descriptors:
            self.assertEquals(descriptor.id, descriptor_sequence[index],
                              "The sorting order was lost during this test case")
            index += 1

    @parameterized.expand([(True,), (False,), ])
    def test_is_parked_double_call(self, is_root):
        """
        Tests whether extra SQL queries were executed during the extra call

        :param is_root: True if the category is root, False otherwise
        """
        descriptors = self._load_category(is_root).descriptors
        self.assertFalse(descriptors.is_parked, "The descriptor list is not parked by default")
        with self.assertLessQueries(0):
            self.assertFalse(descriptors.is_parked, "The descriptor list is not parked by default")

    @parameterized.expand([(True,), (False,), ])
    def test_is_parked_double_call_after_park(self, is_root):
        """
        Tests whether extra SQL queries were executed during the extra call after park

        :param is_root: True if the category is root, False otherwise
        """
        descriptors = self._load_category(is_root).descriptors
        descriptors.park()
        with self.assertLessQueries(0):
            self.assertTrue(descriptors.is_parked, "The descriptor list is parked after park")

    def test_park_interaction(self):
        """
        Tests whether two parking statuses interact with each other
        """
        category1 = self._load_category(True)
        category2 = self._load_category(False)
        category1.descriptors.park()
        self.assertFalse(category2.descriptors.is_parked,
                         "The parking status in the first category relates to the parking status in the second "
                         "category")

    def test_park_general(self):
        """
        Tests that the park method raises RuntimeError in general case (i.e., when no category was selected)
        """
        descriptor_set = ParameterDescriptorSet()
        with self.assertRaises(RuntimeError, msg="The general case must trigger RuntimeError"):
            descriptor_set.park()

    @parameterized.expand([(True,), (False,), ])
    def test_park_quality(self, is_root):
        """
        Tests whether the park method puts indices according to the item position

        :param is_root: True if the category is root, False otherwise
        """
        category = self._load_category(is_root)
        category.descriptors.park()
        expected_index = 1
        for descriptor in category.descriptors:
            self.assertEquals(descriptor.index, expected_index,
                              "The parking indices are badly assigned during the park process")
            expected_index += 1

    @parameterized.expand([(True,), (False,), ])
    def test_park_performance(self, is_root):
        """
        Tests the parking performance

        :param is_root: True if the category is root, False otherwise
        """
        start_time = time()
        category = self._load_category(is_root)
        category.descriptors.park()
        finish_time = time()
        self.assertLessEqual(finish_time - start_time, 1.0, "The parking process is too slow")

    def test_swap_general(self):
        """
        Tests the descriptor swap in general case when no categories were selected
        """
        descriptor_set = ParameterDescriptorSet()
        descriptor1 = self.container.entities[0]
        descriptor2 = self.container.entities[10]
        with self.assertRaises(RuntimeError, msg="Descriptor swap is not possible when no category was selected"):
            descriptor_set.swap(descriptor1, descriptor2)

    @parameterized.expand([(True,), (False,),])
    def test_swap_descriptors_not_parked(self, is_root):
        """
        Tests whether two descriptors can be swapped when the descriptor list is not parked
        """
        category = self._load_category(is_root)
        self.apply_filter('category', category)
        descriptor1 = self.container.entities[1]
        descriptor2 = self.container.entities[2]
        with self.assertRaises(RuntimeError, msg="Can't swap two descriptors"):
            category.descriptors.swap(descriptor1, descriptor2)

    @parameterized.expand(descriptor_swap_provider())
    def test_swap(self, is_root, descriptor_index1, descriptor_index2):
        """
        Provides an ordinary test of the descriptor swap

        :param is_root: True if descriptors should belong to the root category, False otherwise
        :param descriptor_index1: index of the first descriptor to swap within the entity list
        :param descriptor_index2: index of the second descriptor to swap within the entity list
        """
        category = self._load_category(is_root)
        self.apply_filter('category', category)
        expected_order = [descriptor.id for descriptor in self.container.entities]
        expected_order[descriptor_index1], expected_order[descriptor_index2] = \
            expected_order[descriptor_index2], expected_order[descriptor_index1]
        descriptor1 = self.container.entities[descriptor_index1]
        descriptor2 = self.container.entities[descriptor_index2]
        category.descriptors.park()
        category.descriptors.swap(descriptor1, descriptor2)
        index = 0
        for descriptor in category.descriptors:
            self.assertEquals(descriptor.id, expected_order[index],
                              "The descriptor swap was failed")
            index += 1

    @parameterized.expand([(True,), (False,),])
    def test_swap_bad_category(self, is_root):
        """
        Tests whether the swap routine works when some of the descriptors is from another category

        :param is_root: True if descriptors should belong to the root category, False otherwise
        """
        category = self._load_category(is_root)
        category.descriptors.park()
        descriptor1 = category.descriptors[0]
        another_category = self._load_category(not is_root)
        another_category.descriptors.park()
        descriptor2 = another_category.descriptors[0]
        msg = "Descriptors from different categories were successfully swapped"
        with self.assertRaises(ValueError, msg=msg):
            category.descriptors.swap(descriptor1, descriptor2)
        with self.assertRaises(ValueError, msg=msg):
            category.descriptors.swap(descriptor2, descriptor1)

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
        self.assertIsInstance(actual_entity, expected_entity.__class__, msg + ": bad class")
        self.assertEquals(actual_entity.type, expected_entity.type, msg + ": bad entity type")
        self.assertEquals(actual_entity.identifier, expected_entity.identifier, msg + ": bad descriptor identifier")

    def _load_category(self, is_root):
        """
        Loads the category for the parking tests

        :param is_root: True if the category is root
        """
        category = RootCategoryRecord(project=self._record_set_object.optical_imaging)
        if not is_root:
            category_set = category.children
            category_set.alias = 'a'
            category = category_set[0]
        return category

del BaseTestClass
