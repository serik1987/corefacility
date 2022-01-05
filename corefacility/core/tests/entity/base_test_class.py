import os

from django.conf import settings

from core.entity.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException
from core.entity.entity_fields import EntityPasswordManager
from core.tests.media_files_test_case import MediaFilesTestCase


class BaseTestClass(MediaFilesTestCase):
    """
    provides the base class for all test cases

    _check_default_fields and _check_default_change must be re-implemented since they test whether the entity
    re-implement all its default fields after reloading. Given these fields were re-implemented the diagram state
    test cases will be defined automatically by inheritance mechanism. (see test_project how)

    However, field validation tests must be written. Use _test_field function for convenience.
    (see test_project).
    If some field contains file use FileMixin
    If some field contains password use PasswordMixin

    _check_reload function usually tests whether object fields were preserved during the object reload.
    If you need additional checks extend this function (see test_project)

    Use setUpTestData to create all related entities if you want. However, don't forget to call the same method
    from the superclass because it temporally moves all media root files to some safe directory.

    Also, tearDownClass and tearDown method must call similar ones from the superclass.


    DO NOT FORGET to use: del BaseTestClass AFTER EACH subclass declaration
    """

    TEST_CREATE_AND_LOAD = 0
    TEST_CHANGE_CREATE_AND_LOAD = 1
    TEST_CREATE_CHANGE_AND_LOAD = 2
    TEST_CREATE_LOAD_AND_CHANGE = 3

    _entity_object_class = None
    """ The entity object class. New entity object will be created from this class """

    _entity_model_class = None
    """ The entity model class is a Django model that is used for storing entities """

    def test_object_creating_default(self):
        """
        Tests how the object will be created with default values

        :return: nothing
        """
        obj = self.get_entity_object_class()()
        self._check_creating_entity(obj.entity, False)
        self._check_fields_changed(obj.entity, obj.default_field_key)
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="entity update() is possible when it was still creating"):
            obj.entity.update()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="entity delete() is possible when is was still creating"):
            obj.entity.delete()
        obj.create_entity()

    def test_object_creating_default_plus_changed(self):
        """
        This test case will create new entity then changes some entity fields and at last store entity data
        to the database

        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.change_entity_fields()
        self._check_creating_entity(obj.entity, True)
        self._check_fields_changed(obj.entity, obj.entity_fields.keys())
        obj.create_entity()

    def test_object_created_default(self):
        """
        Tests how the object can be created with default values

        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        self._check_created_entity(obj.entity)
        self._check_fields_changed(obj.entity, [])
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="entity object can be created twice"):
            obj.create_entity()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="the 'saved' object can be saved again"):
            obj.entity.update()

    def test_object_created_plus_changed_default(self):
        """
        Tests if the object has been created and correctly changed

        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.change_entity_fields()
        self._check_changed_entity(obj.entity, obj.id)
        self._check_fields_changed(obj.entity, obj.changed_field_key)
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can be created, changed plus created again"):
            obj.create_entity()

    def test_object_created_plus_updated_default(self):
        """
        Tests if the object can be both created and updated

        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.change_entity_fields()
        obj.entity.update()
        self._check_updated_entity(obj.entity, obj.id)
        self._check_fields_changed(obj.entity, [])
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can be re-created when this is created -> changed -> saved"):
            obj.create_entity()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can be re-updated when this is created -> changed -> updated"):
            obj.entity.update()

    def test_object_created_updated_and_loaded_default(self):
        """
        Tests whether the object can be successfully loaded after it has been created and updated

        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.change_entity_fields()
        obj.entity.update()
        obj.reload_entity()
        self._check_reload(obj)
        self._check_fields_changed(obj.entity, [])
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can be re-created when loaded"):
            obj.create_entity()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can be updated when it still loaded and not changed"):
            obj.entity.update()

    def test_object_created_and_loaded_default(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.reload_entity()
        self._check_reload(obj)
        self._check_fields_changed(obj.entity, [])
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can be re-created when loaded"):
            obj.create_entity()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can be updated when it still loaded and not changed"):
            obj.entity.update()

    def test_object_created_loaded_and_changed(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.reload_entity()
        obj.change_entity_fields()
        self._check_changed_entity(obj.entity, obj.id)
        self._check_fields_changed(obj.entity, obj.changed_field_key)
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The entity can't be re-created when 'changing'"):
            obj.create_entity()

    def test_object_created_and_deleted(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.entity.delete()
        self._check_entity_delete(obj)

    def test_object_created_loaded_and_deleted(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.reload_entity()
        obj.entity.delete()
        self._check_entity_delete(obj)

    def test_object_created_changed_and_deleted(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.change_entity_fields()
        obj.entity.delete()
        self._check_entity_delete(obj)

    def _test_field(self, field_name, field_value, updated_value, exception_to_throw, route_number, use_defaults=True,
                    **additional_kwargs):
        """
        Provides the test for a standalone field

        :param field_name: the field name
        :param field_value: the field value
        :param updated_value: another field value to set
        :param exception_to_throw: None if the field value shall be assigned successfully (positive test). An exception
        class if attempt of field assignment must throw an exception (negative test).
        :param route_number: Number of route in the transient state diagram (TEST_CREATE_AND_LOAD,
            TEST_CHANGE_CREATE_AND_LOAD, TEST_CREATE_CHANGE_AND_LOAD, TEST_CREATE_LOAD_AND_CHANGE)
        :param use_defaults: True to use defaults put into the entity_object. False if additional arguments shall be
            put instead of defaults
        :param additional_kwargs: Some additional create object arguments to put
        :return: nothing
        """
        initial_kwargs = {field_name: field_value}
        initial_kwargs.update(additional_kwargs)
        if exception_to_throw is None:
            obj = self.get_entity_object_class()(use_defaults=use_defaults, **initial_kwargs)
        else:
            with self.assertRaises(exception_to_throw,
                                   msg="An invalid value '%s' was successfully assigned to field '%s'" %
                                       (field_value, field_name)):
                self.get_entity_object_class()(use_defaults=use_defaults, **initial_kwargs)
            return
        if route_number == self.TEST_CHANGE_CREATE_AND_LOAD:
            obj.change_entity_fields(use_defaults=False, **{field_name: updated_value})
        obj.create_entity()
        if route_number == self.TEST_CREATE_CHANGE_AND_LOAD:
            obj.change_entity_fields(use_defaults=False, **{field_name: updated_value})
            obj.entity.update()
        obj.reload_entity()
        if route_number == self.TEST_CREATE_LOAD_AND_CHANGE:
            obj.change_entity_fields(use_defaults=False, **{field_name: updated_value})
            obj.entity.update()
        if route_number == self.TEST_CREATE_AND_LOAD:
            last_value = field_value
        else:
            last_value = updated_value
        actual_value = getattr(obj.entity, field_name)
        self.assertEquals(actual_value, last_value,
                          "The value '%s' for field '%s' doesn't either stored or retrieved correctly" %
                          (last_value, field_name))

    def _test_read_only_field(self, field_name, sample_value, throwing_exception=ValueError):
        """
        Checks whether some value can be assigned to the read-only field

        :param field_name: the field name
        :param sample_value: value to assign
        :param throwing_exception: exception to throw
        :return: nothing
        """
        with self.assertRaises(throwing_exception,
                               msg="The read-only field '%s' has been successfully changed" % field_name):
            self.get_entity_object_class()(**{field_name: sample_value})

    def get_entity_object_class(self):
        """
        Returns new entity object class. New entity object will be created exactly from such a class

        :return: the entity object class
        """
        if self._entity_object_class is None:
            raise NotImplementedError("Please, define the _entity_object_class protected variable")
        else:
            return self._entity_object_class

    def get_entity_model_class(self):
        """
        Returns the entity model class. The entity model class is used for storing entities

        :return: the entity model class
        """
        if self._entity_model_class is None:
            raise NotImplementedError("Please, define the _entity_model_class protected variable")
        else:
            return self._entity_model_class

    def _check_creating_entity(self, entity, fields_changed):
        """
        Checks whether all entity fields were in place when the entity is 'CREATING'.
        The entity fields will be checked given that the entity object was created with no keyword arguments.

        :return: nothing
        """
        self.assertIsNone(entity.id, "Entity ID is not None before the entity create")
        self.assertEquals(entity.state, "creating", "Entity state is not 'creating' before the entity create")
        self.assertIsNone(entity._wrapped, "Somebody has wrapped to the entity when the entity is creating")
        if fields_changed:
            self._check_default_change(entity)
        else:
            self._check_default_fields(entity)

    def _check_created_entity(self, entity):
        """
        Checks whether all entity fields were in place when the entity has already been created

        :param entity: the entity to check
        :return: nothing
        """
        self.assertIsNotNone(entity.id, "Entity ID is None when the entity has been created")
        self.assertEquals(entity.state, "saved", "The entity state is not 'saved' after the entity create")
        self._check_default_fields(entity)

    def _check_changed_entity(self, entity, expected_id):
        """
        Checks whether the entity was changed

        :param entity: the entity to check
        :param expected_id: the entity ID to be expected
        :return: nothing
        """
        self.assertEquals(entity.id, expected_id, "The entity ID is not correct")
        self.assertEquals(entity.state, "changed",
                          "The entity state is not 'changed' after entity fields were corrected")
        self._check_default_change(entity)

    def _check_updated_entity(self, entity, expected_id):
        """
        Checks whether the entity can be updated

        :param entity: the entity to be checked
        :return: nothing
        """
        self.assertEquals(entity.id, expected_id, "The entity ID changed during the update process")
        self.assertEquals(entity.state, "saved", "The entity state was not proper")
        self._check_default_change(entity)

    def _check_reload(self, obj):
        """
        Checks whether the entity is successfully and correctly reloaded.

        :param obj: the entity object within which the entity was reloaded
        :return: nothing
        """
        self.assertIsInstance(obj.entity, obj.get_entity_class(),
                              "Unexpected entity class")
        self.assertEquals(obj.entity.id, obj.id, "The entity ID was not properly retrieved")
        self.assertEquals(obj.entity.state, "loaded", "The entity state is not 'loaded' when the entity is loaded")
        self._check_field_consistency(obj)

    def _check_field_consistency(self, obj):
        for name, expected_value in obj.entity_fields.items():
            actual_value = getattr(obj.entity, name)
            self.assertEquals(actual_value, expected_value,
                              "The entity field '%s' doesn't retrieved correctly" % name)

    def _check_entity_delete(self, obj):
        """
        Checks whether the entity is properly deleted

        :param obj: the entity object
        :return: nothing
        """
        self.assertIsNone(obj.entity.id, "The deleted entity still have an ID")
        self.assertEquals(obj.entity.state, "deleted", "The deleted entity has incorrect status")
        with self.assertRaises(EntityOperationNotPermitted, msg="the deleted entity can be created"):
            obj.create_entity()
        with self.assertRaises(EntityOperationNotPermitted, msg="The deleted entity can be saved"):
            obj.entity.update()
        with self.assertRaises(EntityOperationNotPermitted, msg="The deleted entity can be deleted again"):
            obj.entity.delete()
        with self.assertRaises(EntityNotFoundException,
                               msg="The entity can't be deleted carefully since the entity already deleted can be "
                                   "easily re-created"):
            obj.reload_entity()

    def _check_fields_changed(self, entity, field_list):
        """
        Checks whether the certain and only certain fields in the entity was changed

        :param entity: the entity to test
        :param field_list: field list to check in the entity object
        :return: nothing
        """
        self.assertEquals(len(entity._edited_fields), len(field_list),
                          "the Entity._edited_fields doesn't contain appropriate field number")
        for field in field_list:
            self.assertIn(field, entity._edited_fields,
                          "The field '%s' is not within the list of the edited fields")

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        raise NotImplementedError("The _check_default_fields method must be implemented when extending this base class")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param entity: the entity to store
        :return: nothing
        """
        raise NotImplementedError("The _check_default_change method must be implemented when extending this base class")


del MediaFilesTestCase
