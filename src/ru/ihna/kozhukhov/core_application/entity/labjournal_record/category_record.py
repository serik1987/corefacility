from ru.ihna.kozhukhov.core_application.entity.fields.entity_field import EntityField
from ru.ihna.kozhukhov.core_application.entity.fields.date_time_field import DateTimeReadOnlyField
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityNotFoundException

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

    @property
    def children(self):
        """
        All children relating to a given category
        """
        from .record_set import RecordSet
        record_set = RecordSet()
        record_set.parent_category = self
        return record_set

    @property
    def descriptors(self):
        """
        Descriptors that belong immediately to the category
        """
        from ..labjournal_parameter_descriptor.parameter_descriptor_set import ParameterDescriptorSet
        descriptor_set = ParameterDescriptorSet()
        descriptor_set.category = self
        return descriptor_set

    def get_viewed_parameters(self, context):
        """
        Returns list of all viewed parameters

        :param context: the user context to use
        """
        from ..labjournal_viewed_parameter import ViewedParameterSet
        viewed_parameters = ViewedParameterSet()
        viewed_parameters.category = self
        viewed_parameters.user = context
        return viewed_parameters

    def get_search_properties(self, context):
        """
        Returns search properties for a particular user

        :param context: the user context to retrieve
        """
        try:
            from ..labjournal_search_properties import SearchPropertiesSet
            search_properties = SearchPropertiesSet()
            search_properties.category = self
            search_properties.user = context
            return search_properties.get(None)
        except EntityNotFoundException:
            from ..labjournal_search_properties import SearchProperties
            search_properties = SearchProperties()
            search_properties.category = self
            search_properties.user = context
            return search_properties
