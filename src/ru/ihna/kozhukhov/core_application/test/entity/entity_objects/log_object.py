from ....entity.log import Log

from .entity_object import EntityObject


class LogObject(EntityObject):
    """
    Facilitates access to the Log property for testing purpose
    """

    _entity_class = Log

    _default_create_kwargs = {
        "log_address": "/path/to/some/resource"
    }

    _default_change_kwargs = {
        "request_method": "POST",
        "operation_description": "Retrieving some resource information"
    }

    def __init__(self, use_defaults=True, **kwargs):
        super().__init__(use_defaults, **kwargs)
        if use_defaults or "request_date" in kwargs:
            self.entity.request_date.mark()
            self._entity_fields['request_date'] = self.entity.request_date

    @property
    def default_field_key(self):
        return list(super().default_field_key) + ["request_date"]
