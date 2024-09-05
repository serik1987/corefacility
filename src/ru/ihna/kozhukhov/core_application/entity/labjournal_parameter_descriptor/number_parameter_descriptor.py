from ru.ihna.kozhukhov.core_application.models.enums.labjournal_field_type import LabjournalFieldType
from ru.ihna.kozhukhov.core_application.entity.fields import EntityField

from .parameter_descriptor import ParameterDescriptor


class NumberParameterDescriptor(ParameterDescriptor):
    """
    Describes number parameters
    """
    _required_fields = [*ParameterDescriptor._required_fields, 'units']

    _default_type = LabjournalFieldType.number

    _public_field_description = {
        **ParameterDescriptor._public_field_description,
        'units': EntityField(str, min_length=1, max_length=32, description="Measuring units"),
        'default': EntityField(float, description="Default value"),
    }
