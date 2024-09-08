from ru.ihna.kozhukhov.core_application.entity.labjournal_search_properties import SearchProperties

from .entity_object import EntityObject


class SearchPropertiesObject(EntityObject):
    """
    Manipulates the SearchProperties entity for the purpose of automatic testing
    """

    _entity_class = SearchProperties
    """ The entity class that is used to create the entity itself """

    def reload_entity(self):
        """
        Loads the recently saved entity from the database

        :return: nothing
        """
        if self._id is None:
            raise RuntimeError("EntityObject.reload_entity: can't reload the entity that is recently saved")
        entity_set = self._entity.get_entity_set_class()()
        entity_set.category = self._default_create_kwargs['category']
        entity_set.user = self._default_create_kwargs['user']
        self._entity = entity_set.get(self._id)
