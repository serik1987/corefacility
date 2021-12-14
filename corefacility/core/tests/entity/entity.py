from core.entity.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException
from django.test import TestCase


class EntityTest(TestCase):

    _entity_class = None

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
                               msg="the entity has been deleted by it still exists in the external source"):
            another_entity = entity.get_entity_set_class()().get(id)

    def _create_demo_entity(self):
        raise NotImplementedError("EntityTest._create_demo_entity is not implemented")

    def _update_demo_entity(self, entity):
        raise NotImplementedError("EntityTest._update_demo_entity is not implemented")

