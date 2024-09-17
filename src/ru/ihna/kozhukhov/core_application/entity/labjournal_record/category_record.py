from ru.ihna.kozhukhov.core_application.entity.fields.entity_field import EntityField
from ru.ihna.kozhukhov.core_application.entity.fields.date_time_field import DateTimeReadOnlyField
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityNotFoundException

from .record import Record
from ...utils import LabjournalCache


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

    _old_alias = None
    """ The alias at the moment of category create and/or its last update """

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

    def __init__(self, **kwargs):
        """
        Initializes the category.

        :param kwargs:
        """
        super().__init__(**kwargs)
        if 'alias' in self._public_fields:
            self._old_alias = self._public_fields['alias']

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

    def create(self):
        """
        Creates the entity on the database and all its auxiliary sources

        :return: nothing
        """
        super().create()
        self._old_alias = self._public_fields['alias']

    def update(self):
        """
        Updates the entity to the database and all its auxiliary sources

        The update is not possible when the entity state is not 'changed'

        :return: nothing
        """
        LabjournalCache().remove_category(self, self._old_alias)
        super().update()
        self._old_alias = self._public_fields['alias']

    def delete(self):
        """
        Deletes the entity from the database and all its auxiliary sources

        The entity can't be deleted when it still 'creating'

        :return: nothing
        """
        LabjournalCache().remove_category(self, self._old_alias)
        super().delete()
        self._old_alias = None

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
