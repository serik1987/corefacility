from ....models import Log as LogModel

from .model_provider import ModelProvider
from .user_provider import UserProvider


class LogProvider(ModelProvider):
    """
    Provides information exchange between the Log entity and the Django model layer
    """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.log.Log"

    _entity_model = LogModel

    _user_provider = UserProvider()

    _lookup_field = 'id'

    _model_fields = [
        'request_date',
        'log_address',
        'request_method',
        'operation_description',
        'request_body',
        'input_data',
        'user',
        'ip_address',
        'geolocation',
        'response_status',
        'response_body',
        'output_data'
    ]

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
        if entity._user is not None:
            entity._user = self._user_provider.wrap_entity(entity._user)
        return entity
