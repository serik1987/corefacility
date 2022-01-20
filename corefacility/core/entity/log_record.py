from .entity import Entity
from .entity_sets.log_record_set import LogRecordSet
from .entity_providers.model_providers.log_record_provider import LogRecordProvider
from .entity_fields import EntityField, RelatedEntityField, ReadOnlyField, ManagedEntityField, CurrentTimeManager
from .entity_exceptions import EntityOperationNotPermitted


class LogRecord(Entity):
    """
    Defines record that can be attached to every log. Any corefacility module can add one or many records
    for a single log
    """

    _entity_set_class = LogRecordSet

    _entity_provider_list = [
        LogRecordProvider()
    ]

    _required_fields = ["log", "record_time", "level", "message"]

    _public_field_description = {
        "log": RelatedEntityField("core.entity.log.Log", description="Log to this entity relates to"),
        "record_time": ManagedEntityField(CurrentTimeManager, description="Log record time"),
        "level": EntityField(str, min_length=3, max_length=3, description="Log level identifier"),
        "message": EntityField(str, min_length=1, max_length=1024, description="Entity message"),
    }

    def update(self):
        """
        Throws an exception because log records can't be fraud

        :return:
        """
        raise EntityOperationNotPermitted()

    def delete(self):
        """
        Throws an exception because log records can't be removed

        :return:
        """
        raise EntityOperationNotPermitted()
