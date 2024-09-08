from ru.ihna.kozhukhov.core_application.entity.labjournal_viewed_parameter import ViewedParameter

from .entity_object import EntityObject


class ViewedParameterObject(EntityObject):
    """
    An auxiliary class that is used to test the ViewedParameter
    """

    _entity_class = ViewedParameter
    """ The entity class that is used to create the entity itself """

    _category = None
    """ Current category context """

    _user = None
    """ Current user context """

    @classmethod
    def set_default_fields(cls, descriptor, category, user):
        """
        Sets the _default_create_kwargs object

        :param descriptor: related descriptor
        :param category: related category
        :param user: related user
        """
        cls._default_create_kwargs = {
            'descriptor': descriptor,
            'category': category,
            'user': user,
        }

    @classmethod
    def set_default_change_fields(cls, descriptor):
        """
        Sets the _default_change_kwargs object

        :param descriptor: new descriptor to assign
        """
        cls._default_change_kwargs = {
            'descriptor': descriptor,
        }

    def create_entity(self):
        """
        Creates an entity wrapped to this entity object and stores the entity to the database.
        The 'id' property will be updated according to the entity status

        :return: the entity created
        """
        super().create_entity()
        self._category = self.entity.category
        self._user = self.entity.user

    def reload_entity(self):
        """
        Loads the recently saved entity from the database

        :return: nothing
        """
        if self._id is None:
            raise RuntimeError("EntityObject.reload_entity: can't reload the entity that is recently saved")
        entity_set = self._entity.get_entity_set_class()()
        entity_set.category = self._category
        entity_set.user = self._user
        self._entity = entity_set.get(self._id)
