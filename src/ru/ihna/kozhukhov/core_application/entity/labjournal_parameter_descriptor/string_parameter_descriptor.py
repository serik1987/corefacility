from ru.ihna.kozhukhov.core_application.models.enums.labjournal_field_type import LabjournalFieldType
from ru.ihna.kozhukhov.core_application.entity.fields.entity_field import EntityField

from .parameter_descriptor import ParameterDescriptor


class StringParameterDescriptor(ParameterDescriptor):
    """
    Describes string parameters
    """

    _default_type = LabjournalFieldType.string

    _public_field_description = {
        **ParameterDescriptor._public_field_description,
        'default': EntityField(str, min_length=0, max_length=256, description="Default value"),
    }
