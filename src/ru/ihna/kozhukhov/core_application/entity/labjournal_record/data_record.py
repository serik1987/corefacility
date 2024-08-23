from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType

from .record import Record


class DataRecord(Record):
    """
    Represents the record of experimental data
    """

    _default_record_type = LabjournalRecordType.data
    """ Reflects a particular subclass of the labjournal record """

    _required_fields = [
        'parent_category',
        'alias',
        'datetime',
    ]
    """
    If these fields are not filled by the server side's view layer the labjournal record can't be saved
    """
