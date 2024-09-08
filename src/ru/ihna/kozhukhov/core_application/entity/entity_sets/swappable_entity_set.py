from .entity_set import EntitySet


class SwappableEntitySet(EntitySet):
    """
    A mixin for all entity sets that allow swapping

    This is assumed that all entities have 'index' field and the ordering is occured according to the value of this
    field in ascendant order
    """

    def _subcontainer_condition(self):
        """
        Returns True if entity filters are adjusted enough to activate the swapping function
        i.e., when the entity filters are specified some sub-container within which the entities are allowed to swap
        """
        raise NotImplementedError('_container_set_condition')

    def _get_subcontainer_queryset(self):
        """
        Returns the QuerySet object that reveals Django models related to all entities within the container
        """
        raise NotImplementedError("_get_subcontainer_queryset")

    def swap(self, entity1, entity2):
        """
        Changes the descriptor sort order by swapping descriptor1 and descriptor2

        :param entity1: the first entity to swap (an Entity instance or integer)
        :param entity2: the second entity to swap (an Entity instance or integer)
        """
        entity_class = self.get_entity_class()
        if not self._subcontainer_condition():
            raise RuntimeError("To swap two descriptors please, specify the related category")
        entity_models = self._get_subcontainer_queryset()
        if isinstance(entity1, entity_class):
            entity1 = entity1.id
        if isinstance(entity2, entity_class):
            entity2 = entity2.id
        try:
            entity_model1 = entity_models.get(id=entity1)
            entity_model2 = entity_models.get(id=entity2)
        except entity_models.model.DoesNotExist:
            raise ValueError("Can't swap descriptors that don't relate to selected category")
        if entity_model1.index is None or entity_model2.index is None:
            raise RuntimeError("this method can't be invoked because indices are not assigned")
        if entity_model1.index != entity_model2.index:
            entity_model1.index, entity_model2.index = entity_model2.index, entity_model1.index
            entity_model1.save()
            entity_model2.save()