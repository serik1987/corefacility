from ru.ihna.kozhukhov.core_application.models.enums.labjournal_field_type import LabjournalFieldType
from ru.ihna.kozhukhov.core_application.entity.fields import ManagedEntityField, EntityField
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityFieldInvalid

from .parameter_descriptor import ParameterDescriptor
from .discrete_value_manager import DiscreteValueManager


class DiscreteParameterDescriptor(ParameterDescriptor):
    """
    Describes parameter that can take out of several possible values
    """

    _default_type = LabjournalFieldType.discrete

    _public_field_description = {
        **ParameterDescriptor._public_field_description,
        'values': ManagedEntityField(DiscreteValueManager, description="Possible values"),
        'default': EntityField(str, min_length=0, max_length=256, description="Default value"),
    }

    def __setattr__(self, name, value):
        """
        Sets value to the field

        :param name: the field name
        :param value: the field value
        """
        if name == 'default':
            value_is_available = False
            if value is None:
                value_is_available = True
            else:
                for available_value in self.values:
                    if available_value['alias'] == value:
                        value_is_available = True
                        break
            if not value_is_available:
                raise EntityFieldInvalid(name)
        super().__setattr__(name, value)
