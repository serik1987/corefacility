from .raw_sql_query_reader import RawSqlQueryReader
from .query_builders.query_filters import StringQueryFilter
from .model_emulators import ModelEmulator, time_from_db
from ..entity_providers.model_providers.log_record_provider import LogRecordProvider


class LogRecordReader(RawSqlQueryReader):
    """
    Retrieves the log record information from the database and organizes it in form of the LogRecord entity.
    """

    _entity_provider = LogRecordProvider()

    _query_debug = False
    """ Turn this field to True for troubleshooting. """

    def initialize_query_builder(self):
        self.items_builder\
            .add_select_expression("id")\
            .add_select_expression("record_time")\
            .add_select_expression("level")\
            .add_select_expression("message")\
            .add_select_expression("log_id")\
            .add_data_source("core_logrecord")\
            .add_order_term("record_time", self.items_builder.ASC)

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source("core_logrecord")

    def apply_log_filter(self, log):
        """
        Tells the DB engine to send only records attached to a certain log

        :param log: the log to which records shall be attached
        :return: nothing
        """
        for builder in [self.items_builder, self.count_builder]:
            builder.main_filter &= StringQueryFilter("log_id=%s", log.id)

    def create_external_object(self, record_id, record_time, level, message, log_id):
        return ModelEmulator(
            id=record_id,
            record_time=time_from_db(record_time),
            level=level,
            message=message,
            log_id=log_id
        )