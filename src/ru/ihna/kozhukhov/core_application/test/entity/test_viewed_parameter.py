from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor import \
    BooleanParameterDescriptor, NumberParameterDescriptor, StringParameterDescriptor, DiscreteParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_viewed_parameter import ViewedParameter, ViewedParameterSet
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType


from .labjournal_test_mixin import LabjournalTestMixin
from .base_test_class import BaseTestClass
from .entity_objects.viewed_parameter_object import ViewedParameterObject
from ...exceptions.entity_exceptions import EntityFieldInvalid, EntityOperationNotPermitted
from ..data_providers.field_value_providers import put_stages_in_provider


def descriptor_field_test_provider():
    data = [
        ('bool', 'numb', None),
        ('bool', 'stri', None),
        ('bool', 'disc', None),
        ('numb', 'bool', None),
        ('numb', 'stri', None),
        ('numb', 'disc', None),
        ('stri', 'bool', None),
        ('stri', 'numb', None),
        ('stri', 'disc', None),
        ('disc', 'bool', None),
        ('disc', 'numb', None),
        ('disc', 'stri', None),
        ('cate', 'bool', EntityFieldInvalid),
        ('bad',  'bool', EntityFieldInvalid),
    ]
    return put_stages_in_provider(data)


class TestViewedParameter(LabjournalTestMixin, BaseTestClass):
    """
    Tests the viewed parameter class
    """

    sample_category = None
    """ A sample category which view order is going to be adjust """

    sample_boolean_descriptor = None
    """ Some sample descriptor from the descriptor list """

    sample_number_descriptor = None
    """ Some sample descriptor from the descriptor list """

    sample_discrete_descriptor = None
    """ Some sample descriptor from the descriptor list """

    sample_string_descriptor = None
    """ Some sample descriptor from the descriptor list """

    _entity_object_class = ViewedParameterObject
    """ The entity object class. New entity object will be created from this class """

    @classmethod
    def setUpTestData(cls):
        """
        Creates the base test environment
        """
        super().setUpTestData()
        cls.create_base_environment()
        sample_root_category = RootCategoryRecord(project=cls.optical_imaging)
        sample_category_list = sample_root_category.children
        sample_category_list.alias = 'a'
        cls.sample_category = sample_category_list[0]

        cls.sample_boolean_descriptor = BooleanParameterDescriptor(
            category=cls.sample_category,
            identifier="blink",
            description="Моргает ли стимул?",
            required=False,
            record_type=[LabjournalRecordType.data],

        )
        cls.sample_boolean_descriptor.create()

        cls.sample_number_descriptor = NumberParameterDescriptor(
            category=cls.sample_category,
            identifier="spatial_frequency",
            description="Пространственная частота",
            units="цикл/градус",
            required=True,
            record_type=[LabjournalRecordType.data],
        )
        cls.sample_number_descriptor.create()

        cls.sample_discrete_descriptor = DiscreteParameterDescriptor(
            category=cls.sample_category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data],
        )
        cls.sample_discrete_descriptor.create()
        cls.sample_discrete_descriptor.values.add('cw', "По часовой стрелке")
        cls.sample_discrete_descriptor.values.add('ccw', "Против часовой стрелки")

        cls.sample_string_descriptor = StringParameterDescriptor(
            category=cls.sample_category,
            identifier="animal_state",
            description="Состояние животного",
            required=False,
            record_type=[LabjournalRecordType.data, LabjournalRecordType.service]
        )
        cls.sample_string_descriptor.create()

        ViewedParameterObject.set_default_fields(
            cls.sample_boolean_descriptor,
            cls.sample_category,
            TestViewedParameter.users[1],
        )

        ViewedParameterObject.set_default_change_fields(cls.sample_number_descriptor)

    def setUp(self):
        """
        Runs before each test
        """
        super().setUp()
        self.sample_boolean_descriptor = TestViewedParameter.sample_boolean_descriptor
        self.sample_number_descriptor = TestViewedParameter.sample_number_descriptor
        self.sample_discrete_descriptor = TestViewedParameter.sample_discrete_descriptor
        self.sample_string_descriptor = TestViewedParameter.sample_string_descriptor
        self.leader = TestViewedParameter.users[1]
        self.no_leader = TestViewedParameter.users[0]
        self.descriptor_dictionary = {
            'bool': self.sample_boolean_descriptor,
            'numb': self.sample_number_descriptor,
            'stri': self.sample_string_descriptor,
            'disc': self.sample_discrete_descriptor,
            'cate': self.sample_category,
            'bad':  "Hello, World!",
        }

    def test_index_field_read_only(self):
        """
        The index field is read-only
        """
        self._test_read_only_field('index', 10)

    def test_index_field_entities_add(self):
        """
        Tests that the indices to the viewed parameters are assigned in consequtive order when the indices are
        added
        """
        viewed_parameter_set = ViewedParameterSet()
        viewed_parameter_set.category = self.sample_category
        viewed_parameter_set.user = self.leader
        boolean_viewed_parameter = ViewedParameter(
            descriptor=self.sample_boolean_descriptor,
            category=self.sample_category,
            user=self.leader
        )
        boolean_viewed_parameter.create()
        boolean_viewed_parameter = viewed_parameter_set.get(boolean_viewed_parameter.id)
        self.assertEquals(boolean_viewed_parameter.index, 1, "Bad index")

        number_viewed_parameter = ViewedParameter(
            descriptor=self.sample_number_descriptor,
            category=self.sample_category,
            user=self.leader,
        )
        number_viewed_parameter.create()
        boolean_viewed_parameter = viewed_parameter_set.get(boolean_viewed_parameter.id)
        self.assertEquals(boolean_viewed_parameter.index, 1, "Bad index")
        number_viewed_parameter = viewed_parameter_set.get(number_viewed_parameter.id)
        self.assertEquals(number_viewed_parameter.index, 2, "Bad index")

        string_viewed_parameter = ViewedParameter(
            descriptor=self.sample_string_descriptor,
            category=self.sample_category,
            user=self.leader,
        )
        string_viewed_parameter.create()
        boolean_viewed_parameter = viewed_parameter_set.get(boolean_viewed_parameter.id)
        self.assertEquals(boolean_viewed_parameter.index, 1, "Bad index")
        number_viewed_parameter = viewed_parameter_set.get(number_viewed_parameter.id)
        self.assertEquals(number_viewed_parameter.index, 2, "Bad index")
        string_viewed_parameter = viewed_parameter_set.get(string_viewed_parameter.id)
        self.assertEquals(string_viewed_parameter.index, 3, "Bad index")

        discrete_viewed_parameter = ViewedParameter(
            descriptor=self.sample_discrete_descriptor,
            category=self.sample_category,
            user=self.leader,
        )
        discrete_viewed_parameter.create()
        boolean_viewed_parameter = viewed_parameter_set.get(boolean_viewed_parameter.id)
        self.assertEquals(boolean_viewed_parameter.index, 1, "Bad index")
        number_viewed_parameter = viewed_parameter_set.get(number_viewed_parameter.id)
        self.assertEquals(number_viewed_parameter.index, 2, "Bad index")
        string_viewed_parameter = viewed_parameter_set.get(string_viewed_parameter.id)
        self.assertEquals(string_viewed_parameter.index, 3, "Bad index")
        discrete_viewed_parameter = viewed_parameter_set.get(discrete_viewed_parameter.id)
        self.assertEquals(discrete_viewed_parameter.index, 4, "Bad index")

    @parameterized.expand([(0,), (1,), (2,), (3,),])
    def test_index_field_entities_remove(self, parameter_to_remove):
        """
        Tests that valid indices assigned to the viewed parameters when a proper index is removed

        :param parameter_to_remove: cue for the parameter to remove
        """
        test_environment = self._create_all_tested_parameters()
        parameter_to_remove = test_environment[parameter_to_remove]
        test_environment.remove(parameter_to_remove)
        parameter_to_remove.delete()
        test_environment = self._reload_all_tested_parameters(test_environment)
        self.assertIndex(test_environment)

    @parameterized.expand([
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ])
    def test_swap(self, index1, index2):
        """
        Tests the swap method

        :param index1: the first index to swap
        :param index2: the second index to swap
        """
        test_environment = self._create_all_tested_parameters()
        viewed_parameter1 = test_environment[index1]
        viewed_parameter2 = test_environment[index2]
        parameter_set = ViewedParameterSet()
        parameter_set.category = self.sample_category
        parameter_set.user = self.leader
        parameter_set.swap(viewed_parameter1, viewed_parameter2)
        test_environment[index2], test_environment[index1] = viewed_parameter1, viewed_parameter2
        test_environment = self._reload_all_tested_parameters(test_environment)
        self.assertIndex(test_environment)

    @parameterized.expand([
        ('parent', 0), ('parent', 1), ('parent', 2), ('parent', 3),
        ('child', 0),  ('child', 1),  ('child', 2),  ('child', 3),
    ])
    def test_index_field_category_mix(self, another_category, remove_index):
        """
        Tests whether indices that belonged to two categories can interact between each other

        :param another_category: 'child' if another category must be child, 'parent' if another category must be parent
        :param remove_index: index of a removing  viewed parameter
        """
        if another_category == 'parent':
            another_category = self.sample_category.parent_category
        else:
            children = self.sample_category.children
            children.record_type = LabjournalRecordType.category
            another_category = children[0]
        environment1 = self._create_all_tested_parameters()
        environment2 = self._create_all_tested_parameters(category=another_category)
        environment1 = self._reload_all_tested_parameters(environment1)
        environment2 = self._reload_all_tested_parameters(environment2, category=another_category)
        self.assertIndex(environment1)
        self.assertIndex(environment2)
        remove_parameter = environment1[remove_index]
        environment1.remove(remove_parameter)
        remove_parameter.delete()
        environment1 = self._reload_all_tested_parameters(environment1)
        environment2 = self._reload_all_tested_parameters(environment2, category=another_category)
        self.assertIndex(environment1)
        self.assertIndex(environment2)

    @parameterized.expand([(0,), (1,), (2,), (3,),])
    def test_index_field_user_mix(self, remove_index):
        """
        Tests whether indices that belong to two different users can interact between each other

        :param remove_index: index of a removing viewed parameter
        """
        environment1 = self._create_all_tested_parameters()
        environment2 = self._create_all_tested_parameters(user=self.no_leader)
        environment1 = self._reload_all_tested_parameters(environment1)
        environment2 = self._reload_all_tested_parameters(environment2, user=self.no_leader)
        self.assertIndex(environment1)
        self.assertIndex(environment2)
        remove_parameter = environment1[remove_index]
        environment1.remove(remove_parameter)
        remove_parameter.delete()
        environment1 = self._reload_all_tested_parameters(environment1)
        environment2 = self._reload_all_tested_parameters(environment2, user=self.no_leader)
        self.assertIndex(environment1)
        self.assertIndex(environment2)

    @parameterized.expand([(0,), (1,), (2,), (3,), ])
    def test_index_field_project_mix(self, remove_index):
        """
        Tests whether indices that belong to two different projects can interact between each other

        :param remove_index: index of a removing viewed parameter
        """
        category1 = RootCategoryRecord(project=self.optical_imaging)
        category2 = RootCategoryRecord(project=self.the_rabbit_project)
        environment1 = self._create_all_tested_parameters(category=category1)
        environment2 = self._create_all_tested_parameters(category=category2)
        environment1 = self._reload_all_tested_parameters(environment1, category=category1)
        environment2 = self._reload_all_tested_parameters(environment2, category=category2)
        self.assertIndex(environment1)
        self.assertIndex(environment2)
        removing_parameter = environment1[remove_index]
        environment1.remove(removing_parameter)
        removing_parameter.delete()
        environment1 = self._reload_all_tested_parameters(environment1, category=category1)
        environment2 = self._reload_all_tested_parameters(environment2, category=category2)
        self.assertIndex(environment1)
        self.assertIndex(environment2)

    @parameterized.expand(descriptor_field_test_provider())
    def test_descriptor_field(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Provides field test for the descriptor field

        :param initial_value: the first value to assign
        :param final_value: the second value to assign
        :param exception_to_throw: an exception to be thrown
        :param route_number: one out of four basic routes
        """
        initial_value = self.descriptor_dictionary[initial_value]
        final_value = self.descriptor_dictionary[final_value]
        self._test_field('descriptor', initial_value, final_value, exception_to_throw, route_number,
                         assertion_function=self.assertDescriptorEquals)

    def test_category_field_bad_assignment(self):
        """
        Defines what will be happened if one sets bad value to the category
        """
        self._test_field('category', self.sample_boolean_descriptor, None, EntityFieldInvalid,
                         self.TEST_CHANGE_CREATE_AND_LOAD)

    def test_category_field_bad_operation_mode(self):
        """
        Tests what happens if category field is changing when the entity has already been created
        """
        viewed_parameter = ViewedParameter(
            descriptor=self.sample_boolean_descriptor,
            category=self.sample_category,
            user=self.leader,
        )
        viewed_parameter.create()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="the category change should not be allowed at the operation modification"):
            viewed_parameter.category = self.sample_category.parent_category
            viewed_parameter.update()

    def test_user_field_bad_assignment(self):
        """
        Tests what happens if bad value is assigned to the user field
        """
        self._test_field('user', self.sample_category, None, EntityFieldInvalid,
                         self.TEST_CHANGE_CREATE_AND_LOAD)

    def test_user_field_bad_operation_mode(self):
        """
        Tests what happens if the user
        """
        viewed_parameter = ViewedParameter(
            descriptor=self.sample_string_descriptor,
            category=self.sample_category,
            user = self.leader,
        )
        viewed_parameter.create()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="the category change should not be allowed at the operation modification"):
            viewed_parameter.user = self.no_leader
            viewed_parameter.update()

    def _create_all_tested_parameters(self, category=None, user=None):
        """
        Creates test environment for several index tests

        :param category: a category the viewed parameters belong to or None for standard category
        :param user: a used context for which an environment must be created
        """
        if category is None:
            category = self.sample_category
        if user is None:
            user = self.leader
        boolean_viewed_parameter = ViewedParameter(
            descriptor=self.sample_boolean_descriptor,
            category=category,
            user=user
        )
        boolean_viewed_parameter.create()
        number_viewed_parameter = ViewedParameter(
            descriptor=self.sample_number_descriptor,
            category=category,
            user=user,
        )
        number_viewed_parameter.create()
        string_viewed_parameter = ViewedParameter(
            descriptor=self.sample_string_descriptor,
            category=category,
            user=user,
        )
        string_viewed_parameter.create()
        discrete_viewed_parameter = ViewedParameter(
            descriptor=self.sample_discrete_descriptor,
            category=category,
            user=user,
        )
        discrete_viewed_parameter.create()
        return [boolean_viewed_parameter, number_viewed_parameter, string_viewed_parameter, discrete_viewed_parameter]

    def _reload_all_tested_parameters(self, all_tested_parameters, category=None, user=None):
        """
        Reloads all the tested parameters

        :param all_tested_parameters: the tested parameters to reload
        :param category: the reloading category
        :param user: the user context
        """
        if category is None:
            category = self.sample_category
        if user is None:
            user = self.leader
        viewed_parameter_set = ViewedParameterSet()
        viewed_parameter_set.category = category
        viewed_parameter_set.user = user
        return [
            viewed_parameter_set.get(viewed_parameter.id)
            for viewed_parameter in all_tested_parameters
        ]

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        if entity.state == 'creating':
            self.assertIsNone(entity.index, "The entity index should not be assigned until this is created")
        else:
            self.assertEquals(entity.index, 1, "The index should be assigned to 1 when the entity was created")
        self.assertDescriptorEquals(entity.descriptor, self.sample_boolean_descriptor)
        self.assertEquals(entity.category.id, self.sample_category.id, "Category ID mismatch")
        self.assertEquals(entity.user.id, self.leader.id, "User context mismatch")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly changed during the call of the entity_object.change_entity_fields()
        method

        :param entity: the entity to check
        """
        if entity.state == 'creating':
            self.assertIsNone(entity.index, "The entity index should not be assigned until this is created")
        else:
            self.assertEquals(entity.index, 1, "The index should be assigned to 1 when the entity was created")
        self.assertDescriptorEquals(entity.descriptor, self.sample_number_descriptor)
        self.assertEquals(entity.category.id, self.sample_category.id, "Category ID mismatch")
        self.assertEquals(entity.user.id, self.leader.id, "User context mismatch")

    def _check_field_consistency(self, obj):
        """
        Checks field consistency between the original and saved object

        :param obj: the entity object to use
        """
        for name, expected_value in obj.entity_fields.items():
            actual_value = getattr(obj.entity, name)
            if name == 'descriptor':
                self.assertDescriptorEquals(actual_value, expected_value)
            else:
                self.assertEquals(actual_value, expected_value,
                              "The entity field '%s' doesn't retrieved correctly" % name)

    def assertDescriptorEquals(self, actual_descriptor, expected_descriptor):
        self.assertEquals(actual_descriptor.id, expected_descriptor.id, "Descriptor ID mismatch")
        self.assertEquals(actual_descriptor.category.id, expected_descriptor.category.id, "Descriptor category mismatch")
        self.assertEquals(actual_descriptor.category.project.id, expected_descriptor.category.project.id,
                          "Descriptor project mismatch")
        self.assertEquals(actual_descriptor.identifier, expected_descriptor.identifier,
                          "Descriptor identifier mismatch")
        self.assertEquals(actual_descriptor.index, expected_descriptor.index,
                          "Descriptor index mismatch")
        self.assertEquals(actual_descriptor.description, expected_descriptor.description,
                          "Descriptor description mismatch")
        self.assertEquals(actual_descriptor.type, expected_descriptor.type,
                          "Descriptor type mismatch")
        self.assertIsInstance(actual_descriptor, expected_descriptor.__class__, "Descriptor class mismatch")
        self.assertEquals(actual_descriptor.required, expected_descriptor.required,
                          "Descriptor requirement mismatch")
        self.assertEquals(actual_descriptor.default, expected_descriptor.default,
                          "Boolean descriptor mismatch")
        self.assertEquals(set(actual_descriptor.record_type), set(expected_descriptor.record_type),
                          "Record type mismatch")

    def assertIndex(self, viewed_parameter_list):
        """
        Asserts that the index was properly assigned to the viewed parameters

        :param viewed_parameter_list: all viewed parameters loaded for a given category and for a given user
        """
        desired_index = 1
        for viewed_parameter in viewed_parameter_list:
            self.assertEquals(viewed_parameter.index, desired_index, "Bad parameter index")
            desired_index += 1


del BaseTestClass
