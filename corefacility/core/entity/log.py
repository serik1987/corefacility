from datetime import datetime

from . import entity_exceptions as e
from .entity import Entity
from .entity_sets.log_set import LogSet
from .entity_fields import EntityField, RelatedEntityField


class Log(Entity):
    """
    Provides information about request log.

    Each request log is made per each request
    """

    _entity_set_class = LogSet

    _entity_provider_list = []  # TO-DO: describe some log providers

    required_fields = ["request_date"]

    _public_field_description = {
        "request_date": EntityField(datetime, description="Request receiving date"),
        "log_address": EntityField(str, min_length=1, max_length=4096,
                                   description="Log address"),
        "request_method": EntityField(str, min_length=3, max_length=5,
                                      description="Request method"),
        "operation_description": EntityField(str, max_length=4096,
                                             description="Operation description"),
        "request_body": EntityField(str, description="Request body"),
        "input_data": EntityField(str, description="Request input data"),
        "user": RelatedEntityField("core.entity.user.User",
                                   description="Authorized user"),
        "ip_address": EntityField(str, min_length=0, max_length=256,
                                  description="IP address"),
        "geolocation": EntityField(str, min_length=0, max_length=256,
                                   description="Geolocation"),
        "response_status": EntityField(int, min_value=100, max_value=599,
                                       description="HTTP response status"),
        "response_body": EntityField(str, description="Response body"),
        "output_data": EntityField(str, description="Response output data"),
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
        self._current = self

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
        raise NotImplementedError("TO-DO: add log record")
