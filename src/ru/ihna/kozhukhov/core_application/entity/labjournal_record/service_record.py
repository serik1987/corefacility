from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.entity.fields.entity_field import EntityField

from .record import Record


class ServiceRecord(Record):
    """
    Represents service records
    """

    _default_record_type = LabjournalRecordType.service
    """ Reflects a particular subclass of the labjournal record """

    _required_fields = [
        'parent_category',
        'datetime',
    ]
    """
    If these fields are not filled by the server side's view layer the labjournal record can't be saved
    """

    _public_field_description = Record._public_field_description.copy()
    del _public_field_description['alias']
    del _public_field_description['path']
    _public_field_description['name'] = EntityField(
        str,
        max_length=256,
        description="Human-readable record name",
    )
