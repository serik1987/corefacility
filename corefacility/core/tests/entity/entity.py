from datetime import timedelta
from time import sleep

from core.entity.entity import Entity
from core.entity.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException, EntityFieldInvalid
from .entity_providers.dump_entity_provider import DumpEntityProvider
from django.conf import settings
from django.test import TestCase
from django.contrib.staticfiles.finders import find as find_static

from ...entity.entity_fields import EntityPasswordManager


class EntityTest(TestCase):
    """
    First, implement the _create_demo_entity and _update_demo_entity fields
    """

    _entity_class = None

    entity_name = None

    def setUp(self):
        DumpEntityProvider.clear_entity_field_cache()

    def test_create_entity(self):
        entity = self._create_demo_entity()
        self._check_creating_state(entity)
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="object update() is permitted when the object is 'creating'"):
            entity.update()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="object delete() is permitted when then object is 'creating'"):
            entity.delete()
        entity.create()
        self._check_saved_state(entity, msg="after its creating")

    def test_update_entity_from_created(self):
        entity = self._create_demo_entity()
        entity.create()
        id = entity.id
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="object create() is permitted when the object is 'saved'"):
            entity.create()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="object update() is permitted when the object is 'saved'"):
            entity.update()
        self._check_entity_save_transition(entity, id)

    def test_update_entity_from_loaded(self):
        old_entity = self._create_demo_entity()
        old_entity.create()
        entity_set = self.entity_name._entity_set_class()
        id = old_entity.id
        del old_entity
        entity = entity_set.get(id)
        self._check_saved_state(entity, id=None, entity_state="loaded",
                                msg=" after entity loading")
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Able to perform create() operation when the entity is loaded"):
            entity.create()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Able to perform update() operation when the entity is loaded"):
            entity.update()
        self._check_entity_save_transition(entity, id)

    def test_delete_entity_from_created(self):
        entity = self._create_demo_entity()
        entity.create()
        self._provide_entity_delete(entity)

    def test_delete_entity_from_changed(self):
        entity = self._create_demo_entity()
        entity.create()
        self._update_demo_entity(entity)
        self._provide_entity_delete(entity)

    def test_delete_entity_from_loaded(self):
        old_entity = self._create_demo_entity()
        old_entity.create()
        id = old_entity.id
        del old_entity
        entity = self.entity_name.get_entity_set_class()().get(id)
        self._provide_entity_delete(entity)

    def _test_for_empty(self, init_kwargs, name):
        with self.assertRaises(EntityFieldInvalid,
                               msg="'%s' is required but the entity was created when this field left blank" % name):
            entity = self.entity_name(**init_kwargs)
            entity.create()

    def _test_simple_value_assignment(self, init_kwargs, name, value, another_value, exc, stage,
                                      f_lookup="_default_entity_lookup",
                                      f_create_and_set="_default_entity_create_and_set",
                                      f_check="_default_value_check",
                                      f_set="_default_entity_set"):
        init_kwargs_without_value = init_kwargs
        init_kwargs_with_value = init_kwargs.copy()
        init_kwargs_with_value.update({name: value})

        f_lookup = getattr(self, f_lookup)
        f_create_and_set = getattr(self, f_create_and_set)
        f_check = getattr(self, f_check)
        f_set = getattr(self, f_set)

        if stage == 0:
            old_entity = None
            if exc is None:
                old_entity = self.entity_name(**init_kwargs_with_value)
            else:
                with self.assertRaises(exc, msg="The entity can be initialized by invalid value of '%s'" % name):
                    self.entity_name(**init_kwargs_with_value)
            if old_entity is None:
                return
            old_entity.create()
            entity = f_lookup(old_entity)
            f_check(entity, name, value)
        elif stage == 1:
            old_entity = f_create_and_set(exc, init_kwargs_without_value, name, value)
            if old_entity is None:
                return
            old_entity.create()
            entity = f_lookup(old_entity)
            f_check(entity, name, value)
        elif stage == 2:
            old_entity = f_create_and_set(None, init_kwargs_without_value, name, another_value)
            old_entity.create()
            old_entity = f_set(old_entity, exc, name, value)
            if old_entity is None:
                return
            old_entity.update()
            entity = f_lookup(old_entity)
            f_check(entity, name, value)
        elif stage == 3:
            too_old_entity = f_create_and_set(None, init_kwargs_without_value, name, another_value)
            too_old_entity.create()
            old_entity = f_lookup(too_old_entity)
            old_entity = f_set(old_entity, exc, name, value)
            if old_entity is None:
                return
            old_entity.update()
            entity = f_lookup(old_entity)
            f_check(entity, name, value)

    def _check_creating_state(self, entity):
        self.assertIsNone(entity.id, "The entity has non-null ID but it doesn't exist in the database")
        self.assertEquals(entity.state, "creating", "The entity state is not 'creating'")

    def _check_saved_state(self, entity, id=None, msg="", entity_state="saved"):
        self.assertEquals(entity.state, entity_state,
                          "Object state is not 'saved' " + msg)
        if id is None:
            self.assertIsNotNone(entity.id, "The entity does not have ID " + msg)
        else:
            self.assertEquals(entity.id, id, "The entity changed its ID " + msg)

    def _check_entity_save_transition(self, entity, id):
        self._update_demo_entity(entity)
        self._check_saved_state(entity, id=id, entity_state="changed",
                                msg=" after the object that is already created is additionally edited")
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="object create() is permitted when the object is 'changed'"):
            entity.create()
        entity.update()
        self._check_saved_state(entity, id=id,
                                msg=" after the object is created, then editted and next updated")
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="object create() is permitted when the object is 'saved' from being edited"):
            entity.create()

    def _provide_entity_delete(self, entity):
        id = entity.id
        entity.delete()
        self.assertIsNone(entity.id, msg="The entity still have ID even after its deletion")
        self.assertEquals(entity.state, "deleted",
                          msg="The entity doesn't turn to 'deleted' after its deletion")
        with self.assertRaises(EntityOperationNotPermitted, msg="create() operation is permitted on deleted entity"):
            entity.create()
        with self.assertRaises(EntityOperationNotPermitted, msg="update() operation is permitted on deleted entity"):
            entity.update()
        with self.assertRaises(EntityOperationNotPermitted, msg="delete() operation is permitted on deleted entity"):
            entity.delete()
        with self.assertRaises(EntityNotFoundException,
                               msg="the entity has been deleted by it still exists on the external source"):
            entity.get_entity_set_class()().get(id)

    def _create_demo_entity(self):
        raise NotImplementedError("EntityTest._create_demo_entity is not implemented")

    def _update_demo_entity(self, entity):
        raise NotImplementedError("EntityTest._update_demo_entity is not implemented")

    def _default_entity_lookup(self, old_entity: Entity):
        entity_set_class = old_entity.get_entity_set_class()
        entity_set = entity_set_class()
        entity = entity_set.get(old_entity.id)
        return entity

    def _default_value_check(self, entity, name, value):
        self.assertEquals(getattr(entity, name), value,
                          "Valid '%s' value was saved or retrieved incorrectly" % name)

    def _default_entity_set(self, entity, exc, name, value):
        if exc is None:
            setattr(entity, name, value)
            return entity
        else:
            with self.assertRaises(exc, msg="Invalid value is assigned to '%s'" % name):
                setattr(entity, name, value)
            return None

    def _default_entity_create_and_set(self, exc, init_kwargs_without_value, name, value):
        old_entity = self.entity_name(**init_kwargs_without_value)
        old_entity = self._default_entity_set(old_entity, exc, name, value)
        return old_entity

    def _test_load_default_file(self, file_field):
        old_entity = self._create_demo_entity()
        old_entity.create()
        file_manager = getattr(old_entity, file_field)
        url = file_manager.url
        self.assertTrue(url.startswith(settings.STATIC_URL),
                        msg="Error in '%s' field: the default field value is not static file" % file_field)
        file_path = url[len(settings.STATIC_URL):]
        try:
            find_static(file_path)
        except Exception:
            self.fail("The default value of the '%s' property is static file '%s' but Django unable to find it" %
                      (file_field, file_path))

    def _test_password_field(self, password_field):
        old_entity = self._create_demo_entity()
        old_entity.create()
        password = getattr(old_entity, password_field).generate(EntityPasswordManager.ALL_SYMBOLS, 20)
        old_entity.update()
        entity_id = old_entity.id
        entity_set = old_entity.get_entity_set_class()
        del old_entity

        entity = entity_set().get(entity_id)
        entity_password = getattr(entity, password_field)
        self.assertTrue(entity_password.check(password),
                        "The entity doesn't store password for '%s' field" % password_field)
        self.assertFalse(entity_password.check("123"),
                         "The entity accepts any password as password for '%s' field" % password_field)
        entity_password.clear()
        entity.update()

        new_entity = entity_set().get(entity_id)
        entity_password = getattr(new_entity, password_field)
        self.assertFalse(entity_password.check(password),
                         "Unable to properly clear the password for %s field" % password_field)

    def _test_expiry_date_field(self, field_name, duration=10):
        old_entity = self._create_demo_entity()
        old_entity.create()
        dt_field = getattr(old_entity, field_name)
        dt_field.set(timedelta(seconds=duration))
        old_entity.update()
        entity_id = old_entity.id
        entity_set = old_entity.get_entity_set_class()
        del old_entity

        entity = entity_set().get(entity_id)
        dt_field = getattr(entity, field_name)
        self.assertFalse(dt_field.is_expired(),
                         "The '%s' expiration term is less than tested" % field_name)
        sleep(duration)
        self.assertTrue(dt_field.is_expired(),
                        "The '%s' expiration term is higher then tested" % field_name)
        dt_field.clear()
        entity.update()

    def _test_read_only_field(self, field_name):
        entity = self._create_demo_entity()
        with self.assertRaises(ValueError, msg="'%s' field is read-only but successfully set" % field_name):
            setattr(entity, field_name, "klshvkjuh")
        getattr(entity, field_name)

    def _test_foreach(self, name, value_set):
        self._create_several_entities(name, value_set)
        entity_set = self.entity_name.get_entity_set_class()()
        for entity in entity_set:
            actual_value = getattr(entity, name)
            self.assertIn(actual_value, value_set,
                          "The value '%s' of '%s' was found but not set" % (actual_value, value_set))
            value_set.remove(actual_value)
        self.assertTrue(len(value_set) == 0,
                        "The foreach loop did not retrieve all entities")

    def _test_slicing(self, name, value_set):
        self._create_several_entities(name, value_set)
        entity_set = self.entity_name.get_entity_set_class()()
        entity_list = entity_set[3:7]
        self.assertEquals(len(entity_list), 4,
                          "The number of items in the resultant entity list is not the same as expected")
        for entity in entity_list:
            actual_value = getattr(entity, name)
            self.assertIn(actual_value, value_set,
                          "The value '%s' of '%s' was found but not set" % (actual_value, value_set))

    def _test_indexing(self, name, value_set):
        self._create_several_entities(name, value_set)
        entity_set = self.entity_name.get_entity_set_class()()
        entity = entity_set[3]
        actual_value = getattr(entity, name)
        self.assertIn(actual_value, value_set,
                      "The value '%s' of '%s' was found but not set" % (actual_value, value_set))

    def _create_several_entities(self, name, value_set):
        for value in value_set:
            entity = self._create_demo_entity()
            setattr(entity, name, value)
            entity.create()
