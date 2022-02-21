from core.models import ExternalAuthorizationSession as ExternalAuthorizationSessionModel

from .model_provider import ModelProvider
from .corefacility_module_provider import CorefacilityModuleProvider
from ...entity_exceptions import EntityFieldInvalid


class ExternalAuthorizationSessionProvider(ModelProvider):
    """
    Defines the ExternalAuthorizationSession entity will exchange the information
    with the Django model layer.
    """

    _entity_model = ExternalAuthorizationSessionModel

    _lookup_field = "id"

    _model_fields = ["session_key", "session_key_expiry_date"]

    _entity_class = "core.entity.external_authorization_session.ExternalAuthorizationSession"

    _module_provider = CorefacilityModuleProvider()

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
        entity._authorization_module = self._module_provider.wrap_entity(external_object.authorization_module)
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
        external_object = super().unwrap_entity(entity)
        external_object.authorization_module_id = entity._authorization_module.uuid
        if external_object.session_key is None or external_object.session_key == "":
            raise EntityFieldInvalid("External authorization session")
        return external_object
