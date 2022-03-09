from core.entity.entity_providers.model_providers.model_provider import ModelProvider
from imaging.entity.map.map_provider import MapProvider


class PinwheelProvider(ModelProvider):
    """
    Exchanges data and control between the Pinwheel entity and the Django model layer
    """

    _entity_model = "roi.models.Pinwheel"

    _lookup_field = "id"

    _model_fields = ["x", "y"]

    _entity_class = "roi.entity.Pinwheel"

    _map_provider = MapProvider()

    def wrap_entity(self, external_object):
        """
        When the entity information is loaded from the external source, some external_object
        is created (e.g., a django.db.models.Model for database entity provider or dict for
        POSIX users provider). The goal of this function is to transform such external object
        to the entity.

        This method is called by the EntityReader and you are also free to call this method
        by the load_entity function.

        The wrap_entity doesn't retrieve all fields correctly. This is the main and only main
        reason why EntityProvider and EntityReader doesn't want to retrieve the same fields it saved
        and why test_object_created_updated_and_loaded_default and test_object_created_and_loaded
        test cases fail with AssertionError. However, you can override this method in the inherited
        class in such a way as it retrieves all the fields correctly.

        :param external_object: the object loaded using such external source
        :return: the entity that wraps the external object
        """
        entity = super().wrap_entity(external_object)
        entity._map = self._map_provider.wrap_entity(external_object.map)
        return entity


    def unwrap_entity(self, entity):
        """
        To save the entity to the external source you must transform the data containing in
        the entity from the Entity format to another format suitable for such external source
        (e.g., an instance of django.db.models.Model class for database entity provider,
        keys for useradd/usermod function for UNIX users provider etc.). The purpose of this
        function is to make such a conversion.

        :param entity: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        entity_model = super().unwrap_entity(entity)
        entity_model.map_id = entity._map.id
        return entity_model
