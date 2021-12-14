from core.entity.entity_exceptions import EntityOperationNotPermitted
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

    def _create_demo_entity(self):
        raise NotImplementedError("EntityTest._create_demo_entity is not implemented")

    def _update_demo_entity(self, entity):
        raise NotImplementedError("EntityTest._update_demo_entity is not implemented")

