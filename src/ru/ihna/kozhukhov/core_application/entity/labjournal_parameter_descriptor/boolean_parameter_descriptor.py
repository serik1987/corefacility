from ru.ihna.kozhukhov.core_application.models.enums.labjournal_field_type import LabjournalFieldType
from ru.ihna.kozhukhov.core_application.entity.fields.boolean_field import BooleanField

from .parameter_descriptor import ParameterDescriptor


class BooleanParameterDescriptor(ParameterDescriptor):
    """
    Describes boolean parameters.

    Boolean parameters are parameters that can take one out of two possible values: True of False
    """

    _default_type = LabjournalFieldType.boolean

    _public_field_description = ParameterDescriptor._public_field_description.copy()
    _public_field_description['default'] = BooleanField(default=False, description="Default value")
