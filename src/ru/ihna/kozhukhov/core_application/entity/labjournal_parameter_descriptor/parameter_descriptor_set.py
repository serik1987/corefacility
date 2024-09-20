from collections import deque

from django.db.models import F
from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.models import LabjournalParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.entity_sets.swappable_entity_set import SwappableEntitySet
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record import CategoryRecord

from .parameter_descriptor_reader import ParameterDescriptorReader


class ParameterDescriptorSet(SwappableEntitySet):
    """
    Container where all parameter descriptors are stored
    """

    _entity_name = _("Custom parameter descriptor")
    _entity_class = \
        "ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor" + \
        ".parameter_descriptor.ParameterDescriptor"
    _entity_reader_class = ParameterDescriptorReader
    _alias_kwarg = 'identifier'

    _entity_filter_list = {
        'category': (CategoryRecord, None),
        'category_list': (deque, None),
    }

    _index_offset = 1
    """ The smallest index that the descriptor has """

    _is_parked = None
    """ Uses for temporary store of the parking status """

    @property
    def is_parked(self):
        """
        Tests whether the descriptor order mode is automatic or manual

        There are following rules for switching between automatic and manual descriptor order
        1. By default, the descriptor order mode is automatic.
        2. To switch the descriptor order to manual mode you shall call the park() method.
        3. When you add descriptor to the list or remove descriptor from the list the descriptor order MAY BE
            switched to automatic mode again.

        :return: True if the order is manual, False if the order is automatic.
        """
        if self.category is None:
            raise RuntimeError("To check whether the descriptor list is parked you must specify the related category")
        if self._is_parked is not None:
            return self._is_parked
        result = LabjournalParameterDescriptor.objects \
            .filter(category_id=self.category.id, project_id=self.category.project.id)
        is_parked = len(result.filter(index__isnull=True)) == 0
        if is_parked:
            indices = list(result.order_by('index').values_list('index', flat=True))
            expected_indices = list(range(self._index_offset, self._index_offset + len(indices)))
            is_parked = indices == expected_indices
        self._is_parked = is_parked
        return is_parked

    def park(self):
        """
        Switches the descriptor order mode to manual.

        This operation is computationally expensive and not thread-safe.
        """
        if self.category is None:
            raise RuntimeError("To park the descriptor list you must specify the related category")
        descriptor_models = list(LabjournalParameterDescriptor.objects
            .filter(category_id=self.category.id, project_id=self.category.project.id)
            .order_by(F('index').asc(nulls_last=True), 'id'))
        for index in range(len(descriptor_models)):
            descriptor_models[index].index = index + self._index_offset
        LabjournalParameterDescriptor.objects.bulk_update(descriptor_models, ['index'])
        self._is_parked = True

    def _subcontainer_condition(self):
        """
        Returns True if certain container withing which entities can be swapped is specified
        """
        return self.category is not None

    def _get_subcontainer_queryset(self):
        """
        Returns the QuerySet object that reveals Django models related to all entities within the container
        """
        return LabjournalParameterDescriptor.objects \
            .filter(category_id=self.category.id, project_id=self.category.project.id)
