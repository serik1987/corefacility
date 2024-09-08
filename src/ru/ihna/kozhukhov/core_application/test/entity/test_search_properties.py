from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RootCategoryRecord, CategoryRecord
from ru.ihna.kozhukhov.core_application.entity.project import Project
from ru.ihna.kozhukhov.core_application.entity.user import User

from .labjournal_test_mixin import LabjournalTestMixin
from .base_test_class import BaseTestClass
from .entity_objects.search_properties_object import SearchPropertiesObject
from ..data_providers.field_value_providers import put_stages_in_provider
from ...entity.labjournal_search_properties import SearchProperties
from ...exceptions.entity_exceptions import EntityFieldInvalid, EntityOperationNotPermitted, \
    EntityFieldRequiredException


def bad_state_provider():
    return [('saved',), ('changed',), ('loaded',), ]

def properties_provider():
    data = [
        ({}, None,),
        ({'one_property': 3}, None,),
        ({'first_property': 3, 'second_property': 4}, None),
        ([], EntityFieldInvalid,),
        ([1], EntityFieldInvalid),
        ([1, 2,], EntityFieldInvalid),
        ("single_property", EntityFieldInvalid,),
    ]
    return put_stages_in_provider(data)


class TestSearchProperties(LabjournalTestMixin, BaseTestClass):
    """
    Provides test routines for the SearchProperties instance
    """

    _sample_category = None
    """ A category that is usually assigned to all instances of the SearchProperties """

    _sample_user = None
    """ User that mainly holds the category """

    _another_user = None
    """ Auxiliary user for some tests """

    _default_properties = {
        "string_option": "string_value",
        "boolean_option": True,
        "number_option": 3.14,
        "null_option": None,
    }

    _changed_properties = {
        "string_option": "some another value",
        "boolean_option": False,
        "number_option": -3.40,
    }

    _entity_object_class = SearchPropertiesObject
    """ Class of the object that is used to manipulate entities """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_base_environment()
        cls._sample_category = RootCategoryRecord(project=cls.optical_imaging).children[0]
        cls._sample_user = cls.current_user
        cls._another_user = cls.users[9]
        SearchPropertiesObject._default_create_kwargs = {
            'category': cls._sample_category,
            'user': cls._sample_user,
            'properties': cls._default_properties,
        }
        SearchPropertiesObject._default_change_kwargs = {
            'properties': cls._changed_properties
        }

    def test_category_field_negative(self):
        """
        Provides negative test for the category field
        """
        with self.assertRaises(EntityFieldInvalid, msg="User is invalid instance of the category field"):
            obj = self.get_entity_object_class()()
            obj.entity.category = self._sample_user
            obj.create_entity()

    def test_user_field_negative(self):
        """
        Provides negative test for the user field
        """
        with self.assertRaises(EntityFieldInvalid, msg="User is invalid instance of the category field"):
            obj = self.get_entity_object_class()()
            obj.entity.user = self._sample_category
            obj.create_entity()

    @parameterized.expand(bad_state_provider())
    def test_set_category_field_in_bad_state(self, state):
        """
        Tests whether the field can be changed in 'loaded', 'changed' and 'saved' states

        :param state: the changing state
        """
        obj = self._get_sample_properties_for_tests_in_bad_state(state)
        with self.assertRaises(EntityOperationNotPermitted, msg="Category field can't be changed"):
            obj.entity.category = RootCategoryRecord(project=self.optical_imaging)
            obj.entity.update()

    @parameterized.expand(bad_state_provider())
    def test_set_user_field_in_bad_state(self, state):
        """
        Tests whether the field can be changed in 'loaded', 'changed' and 'saved' states

        :param state: the changing state
        """
        obj = self._get_sample_properties_for_tests_in_bad_state(state)
        with self.assertRaises(EntityOperationNotPermitted, msg="User field can't be changed"):
            obj.entity.user = self._another_user
            obj.entity.update()

    def test_category_field_required(self):
        """
        Tests that the category field is required
        """
        search_properties = SearchProperties(
            properties=self._default_properties,
            user=self._sample_user
        )
        with self.assertRaises(EntityFieldRequiredException, msg="The 'category' field must be required"):
            search_properties.create()

    def test_user_field_required(self):
        """
        Tests that the user field is required
        """
        search_properties = SearchProperties(
            properties=self._default_properties,
            category=self._sample_category
        )
        with self.assertRaises(EntityFieldRequiredException, msg="The 'category' field must be required"):
            search_properties.create()

    def test_properties_field_required(self):
        """
        Tests that the properties field is required
        """
        search_properties = SearchProperties(
            user=self._sample_user,
            category=self._sample_category
        )
        with self.assertRaises(EntityFieldRequiredException, msg="The 'category' field must be required"):
            search_properties.create()

    @parameterized.expand(properties_provider())
    def test_properties_field(self, initial_value, exception_to_throw, route_number):
        """
        Test fields for the 'properties' field

        :param initial_value: the value before assignment
        :param exception_to_throw: an exception to be expected or None if no exception is expected
        :param route_number: one out of four possible basic routes
        """
        self._test_field('properties', initial_value, self._default_properties, exception_to_throw,
                         route_number)

    def test_properties_duplicate(self):
        sp1 = SearchProperties(
            category=self._sample_category,
            user=self._sample_user,
            properties=self._default_properties,
        )
        sp1.create()
        sp2 = SearchProperties(
            category=self._sample_category,
            user=self._sample_user,
            properties=self._changed_properties,
        )
        sp2.create()
        sp1 = sp1.category.get_search_properties(sp1.user)  # I mean, reload sp1
        self.assertEquals(sp1.id, sp2.id,
                          "The entity conflict must be resolved by means of update of existing entities")
        self.assertEquals(sp2.state, "saved", "The entity must be saved despite of the conflicts")
        self.assertEquals(sp1.properties, self._changed_properties,
                          "The entity conflict must be resolved by means of update of existing entities")

    def _check_category_and_user_field(self, entity):
        self.assertIsInstance(entity.category, CategoryRecord, "Bad category class")
        self.assertIsInstance(entity.category.project, Project, "Bad project class")
        self.assertIsInstance(entity.user, User, "User mismatch")
        self.assertIsNotNone(entity.category, "The category information is empty")
        self.assertIsNotNone(entity.category.project, "The project information is empty")
        self.assertIsNotNone(entity.user, "The user information is empty")
        self.assertEquals(entity.category.project.id, self.optical_imaging.id, "Loaded project mismatch")
        self.assertEquals(entity.category.id, self._sample_category.id, "Loaded category mismatch")
        self.assertEquals(entity.user.id, self._sample_user.id, "Loaded user mismatch")

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self._check_category_and_user_field(entity)
        self.assertEquals(entity.properties, self._default_properties, "Search properties mismatch")

    def _check_field_consistency(self, obj):
        self._check_category_and_user_field(obj.entity)
        self.assertEquals(obj.entity.properties, obj.entity_fields['properties'], "Search properties mismatch")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly changed during the call of the entity_object.change_entity_fields()
        method

        :param entity: the entity to check
        """
        self._check_category_and_user_field(entity)
        self.assertEquals(entity.properties, self._changed_properties, "Search properties mismatch")

    def _get_sample_properties_for_tests_in_bad_state(self, state):
        """
        Gets sample entity object that is suitable for tests where 'category' or 'user' fields are attempted
        to change in some of the bad state: 'loaded', 'changed' or 'saved'

        :param state: such a bad state
        :return: the SearchPropertiesSet object
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        if state == 'changed':
            obj.entity.properties = self._changed_properties
        if state == 'loaded':
            obj.reload_entity()
        return obj


del BaseTestClass
