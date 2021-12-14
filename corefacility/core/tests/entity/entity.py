from core.entity.entity_exceptions import EntityOperationNotPermitted
from django.test import TestCase


class EntityTest(TestCase):

    _entity_class = None

    def test_state_transition_create(self):
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

    def _check_creating_state(self, entity):
        self.assertIsNone(entity.id, "The entity has non-null ID but it doesn't exist in the database")
        self.assertEquals(entity.state, "creating", "The entity state is not 'creating'")

    def _check_saved_state(self, entity, id=None, msg=""):
        self.assertEquals(entity.state, "saved",
                          "Object state is not 'saved' " + msg)
        if id is None:
            self.assertIsNotNone(entity.id, "The entity does not have ID " + msg)
        else:
            self.assertEquals(entity.id, id, "The entity changed its ID " + msg)

    def _create_demo_entity(self):
        raise NotImplementedError("EntityTest._create_demo_entity is not implemented")

    pass
