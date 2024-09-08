import re

from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.entity.fields import (
    RelatedEntityField,
    EntityAliasField,
    ReadOnlyField,
    EntityField,
    BooleanField,
)

from .parameter_descriptor_set import ParameterDescriptorSet
from .parameter_descriptor_provider import ParameterDescriptorProvider
from .record_type_field import RecordTypeField


class ParameterDescriptor(Entity):
    """
    Represents the parameter descriptor as an entity
    """

    _entity_set_class = ParameterDescriptorSet
    _entity_provider_list = [ParameterDescriptorProvider()]
    _required_fields = [
        'category',
        'identifier',
        'description',
        'required',
        'record_type',
    ]

    _public_field_description = {
        'category': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record.CategoryRecord",
            "A category the descriptor belongs to"),
        'identifier': EntityAliasField(max_length=256, pattern=re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')),
        'index': ReadOnlyField(description="Descriptor index"),
        'description': EntityField(str, min_length=1, max_length=256,
                                   description="Human-readable parameter description"),
        'type': ReadOnlyField(description="Parameter type"),
        'required': BooleanField(default=False, description="The parameter is required to fill"),
        'default': ReadOnlyField(description="Default value"),
        'record_type': RecordTypeField(description="Type of records where the parameter is applicable"),
    }

    _default_type = None
    """
    Default type of the descriptor as defined by its class
    """

    def __init__(self, **kwargs):
        """
        Initializes the entity. The entity can be initialized in the following ways:

        1) Entity(field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by another entities, request views and serializers.
        all values passed to the entity constructor will be validated

        2) Entity(_src=some_external_object, id=value0, field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by entity providers when they try to wrap the object.
        See EntityProvider.wrap_entity for details

        :param kwargs: the fields you want to assign to entity properties
        """
        super().__init__(**kwargs)
        if self._default_type is None:
            raise NotImplementedError("This is the base class: you can't inherit from this")
        else:
            self._public_fields['type'] = self._default_type
