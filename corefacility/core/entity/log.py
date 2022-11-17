from . import entity_exceptions as e
from .entity import Entity
from .log_record import LogRecord, LogRecordSet
from .entity_sets.log_set import LogSet
from .entity_fields import EntityField, RelatedEntityField, ManagedEntityField, CurrentTimeManager, IpAddressField
from .entity_providers.model_providers.log_provider import LogProvider


class Log(Entity):
    """
    Provides information about request log.

    Each request log is made per each request
    """

    TEXT_MAX_LENGTH = 16384

    _entity_set_class = LogSet

    _entity_provider_list = [LogProvider()]

    _required_fields = ["request_date"]

    _public_field_description = {
        "request_date": ManagedEntityField(CurrentTimeManager, description="Request receiving date"),
        "log_address": EntityField(str, min_length=1, max_length=4096,
                                   description="Log address"),
        "request_method": EntityField(str, min_length=3, max_length=7,
                                      description="Request method"),
        "operation_description": EntityField(str, max_length=4096,
                                             description="Operation description"),
        "request_body": EntityField(str, max_length=TEXT_MAX_LENGTH, description="Request body"),
        "input_data": EntityField(str, max_length=TEXT_MAX_LENGTH, description="Request input data"),
        "user": RelatedEntityField("core.entity.user.User",
                                   description="Authorized user"),
        "ip_address": IpAddressField(description="IP address"),
        "geolocation": EntityField(str, min_length=0, max_length=256,
                                   description="Geolocation"),
        "response_status": EntityField(int, min_value=100, max_value=599,
                                       description="HTTP response status"),
        "response_body": EntityField(str, max_length=TEXT_MAX_LENGTH, description="Response body"),
        "output_data": EntityField(str, max_length=TEXT_MAX_LENGTH, description="Response output data"),
    }

    _current = None

    @classmethod
    def current(cls):
        """
        Returns current log.
        "Current log" is a log that contains information about the current request being processed

        :return:
        """
        if cls._current is None:
            raise e.NoCurrentLog()
        return cls._current

    def create(self):
        """
        Creates one log

        :return: nothing
        """
        super().create()
        Log._current = self

    def update(self):
        """
        Updates the log if and only if this is created during the same request as used

        :return:
        """
        if self == self.__class__._current:
            super().update()
        else:
            raise e.EntityOperationNotPermitted()

    def delete(self):
        """
        Throws an exception because this is no way to delete the log.

        :return:
        """
        raise e.EntityOperationNotPermitted()

    def add_record(self, level, message):
        """
        Adds specific record to the log. The record time will be the same as time when this function calls.
        The adding record will be saved to the database immediately.

        :param level: the log level
        :param message: the log message
        :return:
        """
        log_record = LogRecord(level=level, message=message, log=self)
        log_record.record_time.mark()
        log_record.create()

    @property
    def records(self):
        """
        All record sets attached to a given log
        """
        record_set = LogRecordSet()
        record_set.log = self
        return record_set

    def __eq__(self, other):
        """
        Compares two log (for testing purpose only

        :param other: the other log
        :return: nothing
        """
        if isinstance(other, Log):
            return self.id == other.id
        else:
            return False
