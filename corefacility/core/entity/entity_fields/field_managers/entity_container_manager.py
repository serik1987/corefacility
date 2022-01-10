from core.entity.entity_fields.field_managers.entity_value_manager import EntityValueManager
from core.entity.entity import Entity


class EntityContainerManager(EntityValueManager):
    """
    Manages entity fields that are organized as 'containers' for another entities.

    The entity container manager allows to define entity fields that implement so called 'many-to-many
    """

    def add(self, entity: Entity):
        """
        Adds entity to the entity container

        :param entity: the entity to add
        :return: nothing
        """
        raise NotImplementedError("TO-DO: EntityContainerManager.add")

    def remove(self, entity: Entity):
        """
        Removes entity from the entity container

        :param entity: the entity to remove
        :return: nothing
        """
        raise NotImplementedError("TO-DO: EntityContainerManager.remove")
