from django.utils.timezone import localtime

from ....models import LogRecord as LogRecordModel

from .model_provider import ModelProvider
from .log_provider import LogProvider
from ...readers.model_emulators import ModelEmulator


class LogRecordProvider(ModelProvider):
    """
    This component exchanges information between the LogRecord entity and the database.
    """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.log_record.LogRecord"

    _entity_model = LogRecordModel

    _lookup_field = "id"

    _model_fields = ["record_time", "level", "message", "log"]

    _log_provider = LogProvider()

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
        log_record = super().wrap_entity(external_object)
        log_id = external_object.log_id
        log_external_object = ModelEmulator(id=log_id)
        log = self._log_provider.wrap_entity(log_external_object)
        log_record._log = log
        log_record._record_time = localtime(log_record._record_time)
        return log_record
