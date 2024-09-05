from django.db.models import Max
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.models import LabjournalParameterAvailableValue
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_field_type import LabjournalFieldType
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import (
    EntityFieldRequiredException,
    EntityNotFoundException,
    EntityDuplicatedException,
    EntityOperationNotPermitted,
)
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.boolean_parameter_descriptor import \
    BooleanParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.string_parameter_descriptor import \
    StringParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.number_parameter_descriptor import \
    NumberParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.discrete_parameter_descriptor import \
    DiscreteParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.exceptions import \
    DuplicatedValueException

from .base_test_class import BaseTestClass
from .entity_objects.parameter_descriptor_object import ParameterDescriptorObject
from ..data_providers.labjournal_descriptor_providers import (
    category_provider,
    identifier_provider,
    record_type_provider,
    value_alias_provider,
    value_description_provider,
    default_value_provider_for_number_provider,
    default_value_for_discrete_provider
)
from ..data_providers.field_value_providers import (
    put_stages_in_provider,
    string_provider,
    boolean_provider,
)


class TestParameterDescriptor(BaseTestClass):
    """
    Provides test routines for the parameter descriptors
    """

    _entity_object_class = ParameterDescriptorObject
    """ The entity object class. New entity object will be created from this class """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ParameterDescriptorObject.create_base_environment()

    @parameterized.expand(category_provider())
    def test_category_change(self, updated_value, route_number, exception_to_throw):
        """
        Checks whether the category can be changed correctly

        :param updated_value: cue for the new category to assign. Possible values: 'level0', 'level1', 'level2',
            'data_record', 'str'
        :param route_number: the route number to apply (use one of given constants
        :param exception_to_throw: an exception that is expected during the change to the new value
        """
        descriptor_object = self.get_entity_object_class()()
        old_category = descriptor_object.category
        updated_project = descriptor_object.the_rabbit_project
        updated_category = RootCategoryRecord(project=updated_project)
        if updated_value != 'level0':
            updated_category = updated_category.children[1]
            category_set = updated_category.children
            if updated_value == 'level2':
                category_set.alias = 'sample_category'
                updated_category = category_set[0]
            if updated_value == 'data_record':
                category_set.type = LabjournalRecordType.data
                updated_category = category_set[0]
            if updated_value == 'str':
                updated_category = "Hello, World!"
        def wrapped():
            if route_number == self.TEST_CHANGE_CREATE_AND_LOAD:
                descriptor_object.entity.category = updated_category
            descriptor_object.create_entity()
            if route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
                descriptor_object.entity.category = updated_category
                descriptor_object.entity.update()
            if route_number == self.TEST_CHANGE_CREATE_AND_LOAD or route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
                with self.assertRaises(EntityNotFoundException,
                                       msg="The descriptor was not actually moved to the other category"):
                    descriptor_object.reload_entity()
                descriptor_object.category = updated_category
            descriptor_object.reload_entity()
            if route_number == self.TEST_CREATE_LOAD_AND_CHANGE:
                descriptor_object.entity.category = updated_category
                descriptor_object.entity.update()
            if route_number == self.TEST_CREATE_AND_LOAD:
                return old_category
            else:
                return updated_category
        if exception_to_throw is None:
            category = wrapped()
            self.assertEquals(descriptor_object.entity.category.id, category.id, "Category was not loaded")
            self.assertEquals(descriptor_object.entity.category.project.id, category.project.id,
                              "Category project was not loaded")
        else:
            self.assertRaises(exception_to_throw, wrapped)

    @parameterized.expand(identifier_provider())
    def test_identifier(self, value, exception_to_throw, route_number):
        """
        Provides an identifier test

        :param value: an identifier value to substitute
        :param exception_to_throw: an exception that is expected to be throw or None if no exception is expected
        :param route_number: some of the built-in constants that illustrate the route number
        """
        self._test_field('identifier', value, "new_value", exception_to_throw, route_number)

    def test_identifier_required(self):
        """
        Checks that the 'identifier' field is required
        """
        with self.assertRaises(EntityFieldRequiredException, msg="The 'identifier' field must be required"):
            descriptor_object = self.get_entity_object_class()()
            BooleanParameterDescriptor(
                category=descriptor_object.category,
                description="Описание дескриптора",
                required=False,
                record_type=[LabjournalRecordType.data],
            ).create()

    def test_identifier_uniqueness(self):
        """
        Tests that the 'identifier' field is unique among all other fields within the same category
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor_object.create_entity()
        with self.assertRaises(EntityDuplicatedException, msg="Entity duplicate was successfully created"):
            another_descriptor = BooleanParameterDescriptor(
                category=descriptor_object.category,
                identifier=descriptor_object.entity.identifier,
                description="Описание дескриптора",
                required=False,
                record_type=[LabjournalRecordType.data],
            )
            another_descriptor.create()

    def test_identifier_cross_category_uniqueness(self):
        """
        Tests that the 'identifier' field is unique across the whole project
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor_object.create_entity()
        with self.assertRaises(EntityDuplicatedException, msg="Entity duplicate was successfully created"):
            another_descriptor = BooleanParameterDescriptor(
                category=descriptor_object.category.parent_category,
                identifier=descriptor_object.entity.identifier,
                description="Описание другого дескриптора",
                required=True,
                record_type=[LabjournalRecordType.service],
            )
            another_descriptor.create()

    def test_identifier_cross_project_interaction(self):
        """
        Tests whether the descriptors created in one laboratory journal influences on descriptors created on another
        laboratory journal
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor_object.create_entity()
        another_descriptor = BooleanParameterDescriptor(
            category=RootCategoryRecord(project=descriptor_object.the_rabbit_project),
            identifier=descriptor_object.entity.identifier,
            description="Описание другого дескриптора",
            required=True,
            record_type=[LabjournalRecordType.service],
        )
        another_descriptor.create()

    @parameterized.expand(string_provider(1, 256))
    def test_description(self, initial_value, updated_value, exception_to_throw, route_number):
        """
        Provides a test for the "description" field

        :param initial_value: an initial value to substitute
        :param updated_value: an updated value to substitute
        :param exception_to_throw: an exception that is expected to be throw or None if no exception is expected
        :param route_number: some of the built-in constants that illustrate the route number
        """
        self._test_field('description', initial_value, updated_value, exception_to_throw, route_number)

    def test_description_required(self):
        """
        Checks whether the 'description field is required
        """
        with self.assertRaises(EntityFieldRequiredException, msg="The 'identifier' field must be required"):
            descriptor_object = self.get_entity_object_class()()
            BooleanParameterDescriptor(
                category=descriptor_object.category,
                identifier="propofol_induced",
                required=False,
                record_type=[LabjournalRecordType.data],
            ).create()

    @parameterized.expand([
        (BooleanParameterDescriptor, LabjournalFieldType.boolean),
        (StringParameterDescriptor, LabjournalFieldType.string),
        (NumberParameterDescriptor, LabjournalFieldType.number),
        (DiscreteParameterDescriptor, LabjournalFieldType.discrete)
    ])
    def test_type_field(self, descriptor_class, expected_type):
        """
        Checks that the 'type' field reflects a given class and is read-only

        :param descriptor_class: the descriptor class to test
        :param expected_type: an expected type of the parameter descriptor
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = descriptor_class(
            category=descriptor_object.category,
            identifier="propofol_induced",
            description="Описание тестового дескриптора",
            required=False,
            record_type=[LabjournalRecordType.category],
        )
        if descriptor_class == NumberParameterDescriptor:
            descriptor.units = "кг"
        self.assertEquals(descriptor.type, expected_type, "Unexpected descriptor type")
        with self.assertRaises(ValueError, msg="the 'type' field is read-only"):
            descriptor.type = LabjournalFieldType.boolean
        descriptor.create()
        descriptor_id = descriptor.id
        descriptor = descriptor.category.descriptors.get(descriptor_id)
        self.assertEquals(descriptor.state, 'loaded', "The descriptor was not loaded successfully")
        self.assertIsInstance(descriptor, descriptor_class, "Bad descriptor class was assigned during the loading")
        self.assertEquals(descriptor.type, expected_type, "Bad descriptor type was assigned during the loading")

    @parameterized.expand(boolean_provider())
    def test_required_field(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Tests the 'required' field for the validity

        :param initial_value: the initial value to assign
        :param final_value: the value to change
        :param exception_to_throw: an exception that is expected to be thrown or None if no exceptions are expected
        :param route_number: one of the built-in route numbers
        """
        self._test_field('required', initial_value, final_value, exception_to_throw, route_number)

    def test_required_field_required(self):
        """
        Tests whether the 'required' field is required
        """
        descriptor_object = self.get_entity_object_class()()
        with self.assertRaises(EntityFieldRequiredException, msg="The field 'required' doesn't seem to be required"):
            descriptor = BooleanParameterDescriptor(
                category=descriptor_object.category,
                identifier="small_letters",
                description="Описание тестового дескриптора",
                record_type=[LabjournalRecordType.data],
            )
            descriptor.create()

    @parameterized.expand(record_type_provider())
    def test_record_type_field(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Tests the record_type field for validity

        :param initial_value: the first value to assign to this field
        :param final_value: the second value to assign to this field
        :param exception_to_throw: an exception to be expected or None if no exceptions are expected
        :param route_number: defines a stage at which the second value must be assigned
        """
        if exception_to_throw is None:
            descriptor_object = self.get_entity_object_class()(record_type=initial_value)
            if route_number == self.TEST_CHANGE_CREATE_AND_LOAD:
                descriptor_object.entity.record_type = final_value
            descriptor_object.create_entity()
            if route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
                descriptor_object.entity.record_type = final_value
                descriptor_object.entity.update()
            descriptor_object.reload_entity()
            if route_number == self.TEST_CREATE_LOAD_AND_CHANGE:
                descriptor_object.entity.record_type = final_value
            if route_number == self.TEST_CREATE_AND_LOAD:
                expected_value = initial_value
            else:
                expected_value = final_value
            self.assertEquals(set(descriptor_object.entity.record_type), set(expected_value),
                              "The field value doesn't stored successfully")
        else:
            with self.assertRaises(exception_to_throw, msg="The invalid value was successfully passed to the field"):
                self.get_entity_object_class()(record_type=initial_value)

    def test_record_type_required(self):
        """
        Tests whether the record type is required
        """
        descriptor_object = self.get_entity_object_class()()
        with self.assertRaises(EntityFieldRequiredException, msg="The field 'required' doesn't seem to be required"):
            descriptor = BooleanParameterDescriptor(
                category=descriptor_object.category,
                identifier="small_letters",
                description="Описание тестового дескриптора",
                required=False,
            )
            descriptor.create()

    def test_values_in_creating_state(self):
        """
        Tests that all values can't be added when the descriptor object is in the 'creating' state
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="sample_descriptor",
            description="Описание тестового дескриптора",
            required=False,
            record_type=[LabjournalRecordType.data,],
        )
        with self.assertRaises(EntityOperationNotPermitted, msg="can create possible values for the unsaved object"):
            descriptor.values.add('cw', "По часовой стрелке")
        with self.assertRaises(EntityOperationNotPermitted, msg="can destroy possible value for the unsaved object"):
            descriptor.values.remove('cw')
        self.assertEquals(len(descriptor.values), 0, "Some values were auto-added")
        for _ in descriptor.values:
            self.fail("Some values were auto-added")

    def test_values_add_saved_state(self):
        """
        Tests whether possible values can be added when the descriptor object is in 'saved' state
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="sample_descriptor",
            description="Описание тестового дескриптора",
            required=False,
            record_type=[LabjournalRecordType.data,],
        )
        descriptor.create()
        descriptor.values.add("cw", "Clockwise")
        descriptor.values.add("ccw", "Counterclockwise")
        def check_all_values():
            expected_values = {
                'cw': "Clockwise",
                'ccw': "Counterclockwise",
            }
            self.assertEquals(len(descriptor.values), 2, "Not all possible values were added")
            for value in descriptor.values:
                self.assertIn(value['alias'], expected_values, "The value with alias '%s' was lost" % value['alias'])
                expected_description = expected_values[value['alias']]
                self.assertEquals(value['description'], expected_description,
                                  "The value with description '%s' was lost" % value['description'])
                del expected_values[value['alias']]
            self.assertEquals(len(expected_values), 0, "Not all values were added in the list")
        check_all_values()

    def test_values_remove_saved_state(self):
        """
        Tests whether the values can be successfully removed when the descriptor is within the loaded state
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="sample_descriptor",
            description="Описание тестового дескриптора",
            required=False,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor.create()
        descriptor.values.add("cw", "Clockwise")
        descriptor.values.add("ccw", "Counterclockwise")
        descriptor.values.remove('cw')
        self.assertEquals(len(descriptor.values), 1, "The item has not been successfully removed")
        for descriptor_value in descriptor.values:
            if descriptor_value['alias'] == 'cw':
                self.fail("The item has not been successfully removed from the list")

    def test_values_add_loaded_state(self):
        """
        Tests whether the values can be added when the descriptor is within the loaded state
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data,],
        )
        descriptor.create()
        descriptor_id = descriptor.id
        descriptor = descriptor.category.descriptors.get(descriptor_id)
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        expected_values = {
            'cw': "По часовой стрелке",
            'ccw': "Против часовой стрелки",
        }
        self.assertEquals(len(descriptor.values), 2, "Not all values were successfully added")
        for parameter_value in descriptor.values:
            self.assertIn(parameter_value['alias'], expected_values, "An extra value was suddenly added")
            self.assertEquals(parameter_value['description'], expected_values[parameter_value['alias']],
                              "The value description was suddenly changed")
            del expected_values[parameter_value['alias']]
        self.assertEquals(len(expected_values), 0, "Some values were not added to the descriptor")

    def test_values_remove_loaded_state(self):
        """
        Tests when  the possible value can be successfully removed when the entity is in the 'loaded' state
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="small_latins",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data],
        )
        descriptor.create()
        descriptor_id = descriptor.id
        descriptor_set = descriptor.category.descriptors
        descriptor = descriptor_set.get(descriptor_id)
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        descriptor.values.remove('ccw')
        self.assertEquals(len(descriptor.values), 1, "The parameter value was not successfully removed")
        for parameter_value in descriptor.values:
            if parameter_value['alias'] == 'ccw':
                self.fail("The parameter value was not successfully removed")

    def test_values_deleted_state(self):
        """
        Tests the value operations when the entity is in the 'deleted' state
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier='BIG_LATINS',
            description="Я",
            required=True,
            record_type=[LabjournalRecordType.service],
        )
        descriptor.create()
        descriptor_id = descriptor.id
        descriptor_list = descriptor.category.descriptors
        descriptor = descriptor_list.get(descriptor_id)
        descriptor.delete()
        with self.assertRaises(EntityOperationNotPermitted, msg="Can't add value to the deleted descriptor"):
            descriptor.values.add('perp', "Перпендикулярно")
        with self.assertRaises(EntityOperationNotPermitted, msg="Can't remove value from the deleted descriptor"):
            descriptor.values.remove('perp')

    def test_value_read(self):
        """
        Tests whether the possible value can be successfully stored in the database and successfully read from the
        database
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data,],
        )
        descriptor.create()
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        descriptor_id = descriptor.id
        descriptor_list = descriptor.category.descriptors
        descriptor = descriptor_list.get(descriptor_id)
        self.assertEquals(len(descriptor.values), 2, "The parameter values were not loaded")
        expected_values = {
            'cw': "По часовой стрелке",
            'ccw': "Против часовой стрелки",
        }
        for value in descriptor.values:
            value_alias = value['alias']
            value_description = value['description']
            self.assertIn(value_alias, expected_values, "One more value was loaded")
            self.assertEquals(value_description, expected_values[value_alias], "Error in value loading")
            del expected_values[value_alias]
        self.assertEquals(len(expected_values), 0, "Some of the expected values were not loaded from the database")

    def test_removed_value_read(self):
        """
        Tests whether the removed value can still be read from the database
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data,],
        )
        descriptor.create()
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        descriptor.values.add('perp', "Перпендикулярно экрану")
        descriptor_id = descriptor.id
        descriptor_list = descriptor_object.category.descriptors
        descriptor = descriptor_list.get(descriptor_id)
        descriptor.values.remove('perp')
        descriptor = descriptor_list.get(descriptor_id)
        self.assertEquals(len(descriptor.values), 2, "The parameter value was not successfully removed")
        expected_values = {
            'cw': "По часовой стрелке",
            'ccw': "Против часовой стрелки",
        }
        for parameter_value in descriptor.values:
            self.assertIn(parameter_value['alias'], expected_values, "The parameter was suddenly removed with "
                                                                     "some another value")
            self.assertEquals(parameter_value['description'], expected_values[parameter_value['alias']],
                              "The value description was corrupted during the another value remove")
            del expected_values[parameter_value['alias']]
        self.assertEquals(len(expected_values), 0, "The value was not actually removed from the list")

    def test_value_duplication(self):
        """
        Tests whether the duplicated values are allowed
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor.create()
        descriptor.values.add('cw', "По часовой стрелке")
        with self.assertRaises(DuplicatedValueException,
                               msg="Duplicated values were created in the context of the similar descriptor"):
            descriptor.values.add('cw', "Против часовой стрелки")

    def test_value_same_alias_different_descriptors_no_parent(self):
        descriptor_object = self.get_entity_object_class()()

        descriptor1 = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor1.create()
        descriptor1.values.add('cw', "По часовой стрелке")
        descriptor1.values.add('ccw', "Против часовой стрелки")

        descriptor2 = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="rabbit_behavior",
            description="Поведение кролика",
            required=True,
            record_type=[LabjournalRecordType.service,]
        )
        descriptor2.create()
        descriptor2.values.add('cw', "Cool work")
        descriptor2.values.add('dw', "Dummy work")

    @parameterized.expand(value_alias_provider())
    def test_value_alias(self, value_alias, expected_exception):
        """
        Tests the alias of the possible values for the validity

        :param value_alias: the value alias to substitute
        :param expected_exception: what exception is expected to be received; None for no exception
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor.create()
        if expected_exception is None:
            descriptor.values.add(value_alias, "Пример значения кастомного параметра")
            descriptor_id = descriptor.id
            descriptor = descriptor_object.category.descriptors.get(descriptor_id)
            for value in descriptor.values:
                self.assertEquals(value['alias'], value_alias, "The value alias was not stored successfully")
        else:
            with self.assertRaises(expected_exception, msg="Bad value alias was assigned"):
                descriptor.values.add(value_alias, "Пример значения кастомного параметра")

    @parameterized.expand(value_description_provider())
    def test_value_description(self, value_description, expected_exception):
        """
        Tests the value description for all possible values

        :param value_description: a new description to substitute
        :param expected_exception: None if no exception is expected, otherwise an exception to be expected
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor.create()
        if expected_exception is None:
            descriptor.values.add('some_value', value_description)
            descriptor_id = descriptor.id
            descriptor = descriptor_object.category.descriptors.get(descriptor_id)
            for available_value in descriptor.values:
                self.assertEquals(available_value['description'], value_description,
                                  "The value description was not successfully saved")
        else:
            with self.assertRaises(expected_exception, msg="Bad string was successfully used as description"):
                descriptor.values.add('some_value', value_description)

    def test_value_remove_number_id(self):
        """
        Tests whether the value can be removed by its number ID
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor.create()
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        descriptor.values.add('perp', "Перпендикулярно экрану")
        value_id = None
        for value in descriptor.values:
            if value['alias'] == 'perp':
                value_id = value['id']
        self.assertIsNotNone(value_id, "The value was not successfully added")
        descriptor_id = descriptor.id
        descriptor = descriptor_object.category.descriptors.get(descriptor_id)
        descriptor.values.remove(value_id)
        descriptor = descriptor_object.category.descriptors.get(descriptor_id)
        expected_values = {
            'cw': "По часовой стрелке",
            'ccw': "Против часовой стрелки",
        }
        self.assertEquals(len(descriptor.values), 2, "The values were not removed successfully")
        for value in descriptor.values:
            self.assertIn(value['alias'], expected_values, "The value was corrupted during the another value remove")
            self.assertEquals(value['description'], expected_values[value['alias']],
                              "The value description was corrupted during the another value remove")
            del expected_values[value['alias']]
        self.assertEquals(len(expected_values), 0, "The values were not removed successfully")

    @parameterized.expand([('alias',), ('max_id',),])
    def test_remove_non_existent_value(self, value_id):
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor.create()
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        if value_id == 'max_id':
            value_id = \
                LabjournalParameterAvailableValue.objects.filter(descriptor_id=descriptor.id).aggregate(Max('id')) \
                ['id__max'] + 1
        with self.assertRaises(EntityOperationNotPermitted):
            descriptor.values.remove(value_id)

    def test_possible_values_autoremove(self):
        """
        Tests whether all possible values will be removed from the table together with the descriptor itself
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor.create()
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        descriptor.delete()
        self.assertEquals(len(LabjournalParameterAvailableValue.objects.all()), 0,
                          "Descriptor values are not automatically deleted together with the descriptor")


    def test_descriptor_conflicts(self):
        descriptor_object = self.get_entity_object_class()()
        descriptor1 = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data, ],
        )
        descriptor1.create()
        descriptor2 = DiscreteParameterDescriptor(
            category=descriptor_object.category,
            identifier="rabbit_behavior",
            description="Поведение кролика",
            required=True,
            record_type=[LabjournalRecordType.service, ]
        )
        descriptor2.create()

        descriptor1.values.add('cw', "По часовой стрелке")
        descriptor2.values.add('cw', "Cool work")
        descriptor1.values.add('ccw', "Против часовой стрелки")
        descriptor2.values.add('dw', "Dummy work")

        descriptor1 = descriptor_object.category.descriptors.get(descriptor1.id)
        expected_values = {
            'cw': "По часовой стрелке",
            'ccw': "Против часовой стрелки",
        }
        self.assertEquals(len(descriptor1.values), 2, "Values conflict")
        for value in descriptor1.values:
            self.assertIn(value['alias'], expected_values, "Values conflict")
            self.assertEquals(value['description'], expected_values[value['alias']], "Values conflict")
            del expected_values[value['alias']]
        self.assertEquals(len(expected_values), 0, "Values conflict")

        descriptor2 = descriptor_object.category.descriptors.get(descriptor2.id)
        expected_values = {
            'cw': "Cool work",
            'dw': "Dummy work",
        }
        for value in descriptor2.values:
            self.assertIn(value['alias'], expected_values, "Values conflict")
            self.assertEquals(value['description'], expected_values[value['alias']], "Values conflict")
            del expected_values[value['alias']]
        self.assertEquals(len(expected_values), 0, "Values conflict")

    @parameterized.expand([
        (BooleanParameterDescriptor, AttributeError,),
        (NumberParameterDescriptor, AttributeError,),
        (StringParameterDescriptor, AttributeError,),
        (DiscreteParameterDescriptor, None,),
    ])
    def test_values_different_classes(self, class_name, exception_to_throw):
        """
        Tests whether different classes has values field

        :param class_name: a class to test
        :param exception_to_throw: an exception that is expected to throw
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = class_name(
            category=descriptor_object.category,
            identifier="small_latins",
            description="Тестовое описание",
            required=True,
            record_type=[LabjournalRecordType.category,],
        )
        if class_name == NumberParameterDescriptor:
            descriptor.units = "kg"
        descriptor.create()
        if exception_to_throw is None:
            descriptor.values.add("alias", "описание")
        else:
            with self.assertRaises(exception_to_throw, msg="The field must not exist for a given type"):
                descriptor.values.add("alias", "описание")

    @parameterized.expand([
        (BooleanParameterDescriptor, AttributeError),
        (NumberParameterDescriptor, None,),
        (StringParameterDescriptor, AttributeError),
        (DiscreteParameterDescriptor, AttributeError),
    ])
    def test_units_field_different_classes(self, class_name, exception_to_throw):
        """
        Tests whether different classes has units field

        :param class_name: name of the class to test
        :param exception_to_throw: None if no exceptions were expected, otherwise an exception to throw
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = class_name(
            category=descriptor_object.category,
            identifier="digits123",
            description="Иное описание",
            required=False,
            record_type=[LabjournalRecordType.category, LabjournalRecordType.data,],
        )
        if exception_to_throw is None:
            descriptor.units = "кг"
            descriptor.create()
        else:
            with self.assertRaises(exception_to_throw, msg="The field must throw an exception"):
                descriptor.units = "кг"

    def test_units_field_required(self):
        """
        Tests whether the units field is mandatory
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = NumberParameterDescriptor(
            category=descriptor_object.category,
            identifier="digits123",
            description="Моё описание",
            required=True,
            record_type=[LabjournalRecordType.category, LabjournalRecordType.data,],
        )
        with self.assertRaises(EntityFieldRequiredException, msg="The units field must be mandatory"):
            descriptor.create()

    @parameterized.expand(string_provider(1, 32))
    def test_units_field(self, old_value, new_value, exception, route_number):
        """
        Main test for the units field

        :param old_value: the old value to assign
        :param new_value: the second value to assign
        :param exception: an exception that is expected to throw, or None if no exception is expected
        :param route_number: one out of four basic scenario
        """
        descriptor_object = self.get_entity_object_class()()
        descriptor = NumberParameterDescriptor(
            category=descriptor_object.category,
            identifier="sample_rate",
            description="Частота оцифровки",
            required=True,
            record_type=[LabjournalRecordType.data,],
        )
        if exception is None:
            descriptor.units = old_value
            if route_number == self.TEST_CHANGE_CREATE_AND_LOAD:
                descriptor.units = new_value
            descriptor.create()
            if route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
                descriptor.units = new_value
                descriptor.update()
            descriptor_id = descriptor.id
            descriptor = descriptor_object.category.descriptors.get(descriptor_id)
            if route_number == self.TEST_CREATE_LOAD_AND_CHANGE:
                descriptor.units = new_value
            if route_number == self.TEST_CREATE_AND_LOAD:
                expected_value = old_value
            else:
                expected_value = new_value
            self.assertEquals(descriptor.units, expected_value, "The 'units' value was damaged")
        else:
            with self.assertRaises(exception, msg="Attempt to assign the bad value"):
                descriptor.units = old_value

    @parameterized.expand(boolean_provider())
    def test_default_field_for_boolean(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Tests the 'default' field for the BooleanParameterDescriptor

        :param initial_value: the first value to assign to the field
        :param final_value: the second value to assign to the field
        :param exception_to_throw: an exception to be expected or None if no exception is expected
        :param route_number: one of the predefined routes
        """
        self._test_field('default', initial_value, final_value, exception_to_throw, route_number)

    @parameterized.expand(default_value_provider_for_number_provider())
    def test_default_field_for_number(self, initial_number, final_number, exception_to_throw, route_number):
        """
        Tests the 'default' field for the NumberParameterDescriptor

        :param initial_number: the first value to assign to the field
        :param final_number: the second value to assign to the field
        :param exception_to_throw: an exception to be expected or None if not exception is expected
        :param route_number: one of the predefined routes
        """
        category = self.get_entity_object_class()().category
        descriptor = NumberParameterDescriptor(
            category=category,
            identifier="concentration",
            description="Концентрация пропофола",
            required=False,
            units="мг/кг",
            record_type=[LabjournalRecordType.service,],
        )
        if exception_to_throw is None:
            descriptor.default = initial_number
            if route_number == self.TEST_CHANGE_CREATE_AND_LOAD:
                descriptor.default = final_number
            descriptor.create()
            if route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
                descriptor.default = final_number
                descriptor.update()
            descriptor_id = descriptor.id
            descriptor = category.descriptors.get(descriptor_id)
            if route_number == self.TEST_CREATE_LOAD_AND_CHANGE:
                descriptor.default = final_number
            if route_number == self.TEST_CREATE_AND_LOAD:
                expected_number = initial_number
            else:
                expected_number = final_number
            if descriptor.default is not None:
                self.assertIsInstance(descriptor.default, float, "Bad type for the default number")
            self.assertEquals(descriptor.default, expected_number, "The default value was corrupted during the save")
        else:
            with self.assertRaises(exception_to_throw, msg="The exception was not thrown"):
                descriptor.default = initial_number

    @parameterized.expand(
        string_provider(min_length=0, max_length=256) +
        put_stages_in_provider([("Sample text", None, None,),])
    )
    def test_default_field_string(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Tests the 'default' field for the StringParameterDescriptor

        :param initial_value: an initial value to assign
        :param final_value: a final value to assign
        :param exception_to_throw: an exception that is expected to throw or None if not exception is expected
        :param route_number: one out of four base routes
        """
        category = self.get_entity_object_class()().category
        descriptor = StringParameterDescriptor(
            category=category,
            identifier="small_latins",
            description="Описание кастомного параметра",
            record_type=[LabjournalRecordType.data,],
            required=True,
        )
        if exception_to_throw is None:
            descriptor.default = initial_value
            if route_number == self.TEST_CHANGE_CREATE_AND_LOAD:
                descriptor.default = final_value
            descriptor.create()
            if route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
                descriptor.default = final_value
                descriptor.update()
            descriptor_id = descriptor.id
            descriptor = category.descriptors.get(descriptor_id)
            if route_number == self.TEST_CREATE_LOAD_AND_CHANGE:
                descriptor.default = final_value
            if route_number == self.TEST_CREATE_AND_LOAD:
                expected_value = initial_value
            else:
                expected_value = final_value
            if expected_value is not None:
                self.assertIsInstance(descriptor.default, str, "The default value has bad type")
            self.assertEquals(descriptor.default, expected_value, "The default value doesn't store correctly")
        else:
            with self.assertRaises(exception_to_throw, msg="Bad value has been successfully assigned"):
                descriptor.default = initial_value

    @parameterized.expand(default_value_for_discrete_provider())
    def test_default_field_for_discrete(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Tests the 'default' field for the DiscreteParameterDescriptor

        :param initial_value: the first value to assign
        :param final_value: the second value to assign
        :param exception_to_throw: an exception to be expected or None if no exception is expected
        :route_number: one of the three base routes, excluding TEST_CHANGE_CREATE_AND_LOAD
        """
        category = self.get_entity_object_class()().category
        descriptor = DiscreteParameterDescriptor(
            category=category,
            identifier="grating_rotation",
            description="Направление вращения решётки",
            required=True,
            record_type=[LabjournalRecordType.data,],
        )
        descriptor.create()
        descriptor.values.add('cw', "По часовой стрелке")
        descriptor.values.add('ccw', "Против часовой стрелки")
        if exception_to_throw is None:
            descriptor.default = initial_value
            if route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
                descriptor.default = final_value
            descriptor.update()
            descriptor_id = descriptor.id
            descriptor = category.descriptors.get(descriptor_id)
            if route_number == self.TEST_CREATE_LOAD_AND_CHANGE:
                descriptor.default = final_value
            if route_number == self.TEST_CREATE_AND_LOAD:
                expected_value = initial_value
            else:
                expected_value = final_value
            if expected_value is not None:
                self.assertIsInstance(descriptor.default, str, "Bad value class")
            self.assertEquals(descriptor.default, expected_value, "The value has not been properly stored")
        else:
            with self.assertRaises(exception_to_throw, msg="Bad value has been successfully assigned"):
                descriptor.default = initial_value

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(entity.identifier, 'id', "Entity identifier mismatch")
        self.assertEquals(entity.description, "Описание сущности", "Entity description mismatch")
        self.assertEquals(entity.required, False, "Field required mismatch")
        self.assertIn(LabjournalRecordType.data, entity.record_type, "Record type mismatch")
        self.assertNotIn(LabjournalRecordType.service, entity.record_type, "Record type mismatch")
        self.assertNotIn(LabjournalRecordType.category, entity.record_type, "Record type mismatch")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly changed during the call of the entity_object.change_entity_fields()
        method

        :param entity: the entity to check
        """
        self.assertEquals(entity.identifier, 'id2', "Entity identifier mismatch")
        self.assertEquals(entity.description, "Другое описание сущности", "Entity description mismatch")
        self.assertEquals(entity.required, True, "Field required mismatch")
        self.assertIn(LabjournalRecordType.data, entity.record_type, "Record type mismatch")
        self.assertIn(LabjournalRecordType.service, entity.record_type, "Record type mismatch")
        self.assertNotIn(LabjournalRecordType.category, entity.record_type, "Record type mismatch")


del BaseTestClass
