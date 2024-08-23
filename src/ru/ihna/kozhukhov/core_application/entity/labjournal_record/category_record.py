from ru.ihna.kozhukhov.core_application.entity.fields.entity_field import EntityField
from ru.ihna.kozhukhov.core_application.entity.fields.read_only_field import ReadOnlyField
from ru.ihna.kozhukhov.core_application.entity.fields.date_time_field import DateTimeReadOnlyField
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType

from .record import Record


class CategoryRecord(Record):
    """
    Represents the category record
    """

    _default_record_type = LabjournalRecordType.category
    """ Reflects a particular subclass of the labjournal record """

    _required_fields = [
        'parent_category',
        'alias',
    ]
    """
    If these fields are not filled by the server side's view layer the labjournal record can't be saved
    """

    _public_field_description = Record._public_field_description.copy()
    _public_field_description.update({
        'datetime': DateTimeReadOnlyField(description="Date and time of the very first record"),
        'finish_time': DateTimeReadOnlyField(description="Date and time of the very last record"),
        'base_directory': EntityField(
            str,
            max_length=256,
            default='.',
            description="Base directory (relatively to the base directory of the parent category)"
        )
    })
