from ....entity.log_record import LogRecord

from .entity_set_object import EntitySetObject


class LogRecordSetObject(EntitySetObject):
    """
    Creates expected set of log records.

    The test success will be judged on comparison of this expected log record set with actual one from
    core.entity.entity_set.log_record_set.LogRecordSet class.
    """

    MIN_LOG_NUMBER = 6

    _entity_class = LogRecord

    _log_set_object = None

    def __init__(self, log_set_object, _entities=None):
        """
        Initializes the expected log record set

        :param log_set_object: the log set object containing at least six logs
        :param _entities: for service use only
        """
        if len(log_set_object) < self.MIN_LOG_NUMBER:
            raise ValueError("The log set object passed as an argument is too small")
        self._log_set_object = log_set_object
        super().__init__(_entities)

    def clone(self):
        """
        Creates an exact copy of the entity set objects

        :return: an exact copy of the entity set objects
        """
        return self.__class__(self._log_set_object, _entities=self._entities)

    def filter_by_log(self, log):
        self._entities = list(filter(lambda record: record.log.id == log.id, self._entities))

    def data_provider(self):
        """
        Defines keyword arguments that will be used to create the testing log records

        :return: nothing
        """
        return [
            dict(log=self._log_set_object[0], level="DEB", message="Message 1 for log 1"),
            dict(log=self._log_set_object[0], level="ERR", message="Message 2 for log 1"),
            dict(log=self._log_set_object[1], level="INF", message="Message 1 for log 2"),
            dict(log=self._log_set_object[1], level="CRT", message="Message 2 for log 2"),
            dict(log=self._log_set_object[2], level="WAR", message="The only message for log 3"),
            dict(log=self._log_set_object[3], level="WAR", message="The only message for log 4"),
        ]

    def _new_entity(self, **entity_fields):
        """
        Creates new entity with given initial parameters

        :param entity_fields: the initial parameters passed here from the data provider
        :return: nothing
        """
        log_record = super()._new_entity(**entity_fields)
        log_record.record_time.mark()
        return log_record
