from core.entity.log_record import LogRecord

from .entity_object import EntityObject


class LogRecordObject(EntityObject):
    """
    This component facilitates creation of log records for testing purpose.
    """

    _entity_class = LogRecord

    _default_create_kwargs = {
        "level": "DBG",
        "message": "This is my first log record message"
    }

    _default_change_kwargs = {
        "level": "ERR",
        "message": "The message was suddenly editted"
    }

    def __init__(self, use_defaults=True, **kwargs):
        """
        Creates the entity object that results to creating an entity.

        :param use_defaults: if True, the constructor will use the _default_create_kwargs fields. Otherwise this
        class property will be ignored
        :param kwargs: Any additional field values that shall be embedded to the entity or 'id' that reflects the
        entity ID
        """
        super().__init__(use_defaults, **kwargs)
        if use_defaults or "record_time" in kwargs:
            self.mark_record_time()

    def mark_record_time(self):
        """
        Puts the current time to the 'record_time' field of the overlapped entity

        :return: nothing
        """
        self.entity.record_time.mark()
        self._entity_fields['record_time'] = self.entity.record_time

    @property
    def default_field_key(self):
        """
        Returns keys from all default keyword args, just for additional checks

        :return:
        """
        return list(super().default_field_key) + ["record_time"]
