from collections import OrderedDict

from rest_framework.serializers import\
    ChoiceField, SlugField, ReadOnlyField, CharField, DateTimeField, DurationField, BooleanField
from rest_framework.exceptions import ValidationError

from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.serializers import EntitySerializer
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import \
    DataRecord, ServiceRecord, CategoryRecord, RootCategoryRecord


class RecordSerializer(EntitySerializer):
    """
    This is the base class for serializers for the data, service and category labjournal records.
    """

    entity_classes = {
        'data': DataRecord,
        'service': ServiceRecord,
        'category': CategoryRecord,
        'root': RootCategoryRecord,
    }
    """ List of all available records """

    id = ReadOnlyField(
        label="Record ID",
        help_text="Numerical ID of the record",
    )

    type = ChoiceField(
        source="type.name",
        label="Record type",
        help_text="'data' for experimental data record, 'service' for service record, 'category' for category",
        choices=['data', 'service', 'category'],
    )

    level = ReadOnlyField(
        label="Record level",
        help_text="Level of root record is zero, level for any other record is level for root record plus 1"
    )

    alias = SlugField(
        required=False,
        label="Record alias",
        help_text="String ID of the record (not for service records)",
        max_length=64,
    )

    path = ReadOnlyField(
        required=False,
        label="Record path",
        help_text="String ID of the record (not for service records)",
    )

    name = CharField(
        required=False,
        label="Name",
        help_text="Human-readable record name (for service records only)",
        max_length=256,
        allow_blank=True,
    )

    datetime = DateTimeField(
        required=False,
        label="Record time",
        help_text="Record date and time (for a category - date and time of the very first child record)",
    )

    relative_time = DurationField(
        read_only=True,
        label="Relative time",
        help_text="Duration from the date and time of the very first record within the parent category and "
                  "date and time of the very first record",
    )

    checked = BooleanField(
        default=False,
        label="Check status",
        help_text="Whether the record has been checked by the user or not",
    )

    finish_time = DateTimeField(
        read_only=True,
        label="Category finish time (defined for categories only)",
        help_text="Date and time of the very last child record",
    )

    base_directory = CharField(
        required=False,
        label="Base directory",
        help_text="Relative path to the base directory, relatively to the base directory of a current record. "
                  "For root record - relatively to the LABJOURNAL_BASEDIR settings directory",
        max_length=256,
    )

    comments = CharField(
        required=False,
        label="Comments",
        help_text="Any extra information that did not put into a given paradigm",
        max_length=16_384,
    )

    def validate_base_directory(self, value):
        """
        Provides an additional validation for the base directory of the record

        :param value: value of the base directory to validate
        """
        print(value)
        raise NotImplementedError('validate_base_directory')

    def validate(self, data):
        """
        Provides an additional validation to validation algorithms defined by the serializer fields.

        :param data: the request data before the additional validation
        :return: the request data after the additional validation
        """
        error_list = OrderedDict()
        if self.instance is None:
            record_type = getattr(LabjournalRecordType, data['type']['name'])
        else:
            record_type = self.instance.type

        if record_type != LabjournalRecordType.service and 'alias' not in data:
            error_list['alias'] = self.error_messages['required']
        if record_type == LabjournalRecordType.service and 'alias' in data:
            del data['alias']

        if len(error_list) > 0:
            raise ValidationError(error_list)
        return data

    def to_representation(self, record):
        """
        Transforms the laboratory journal record to Python primitives

        :param record: The laboratory journal record
        :return: a dictionary of Python primitives
        """
        record_data = super().to_representation(record)
        # Turning off the time zone support for all labjournal records
        if record_data['datetime'] is not None:
            record_data['datetime'] = record_data['datetime'].split('+')[0]
        if 'finish_time' in record_data and record_data['finish_time'] is not None:
            record_data['finish_time'] = record_data['finish_time'].split('+')[0]
        for parameter_name, parameter_value in record.customparameters.items():
            record_data['custom_%s' % parameter_name] = parameter_value
        return record_data

    def create(self, data):
        self.entity_class = self.entity_classes[data['type']['name']]
        del data['type']
        data = OrderedDict(
            parent_category=self.context['request'].parent_category,
            user=self.context['request'].user,
            **data,
        )
        record = super().create(data)
        self.entity_class = None
        return record
