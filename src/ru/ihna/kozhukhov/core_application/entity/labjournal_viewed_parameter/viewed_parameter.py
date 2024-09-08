from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityOperationNotPermitted
from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.entity.fields import ReadOnlyField, RelatedEntityField

from .viewed_parameter_set import ViewedParameterSet
from .viewed_parameter_provider import ViewedParameterProvider


class ViewedParameter(Entity):
    """
    Represents the custom parameter that will be shown in the category view table
    """

    _entity_set_class = ViewedParameterSet
    """ Provides a container where all viewed parameters are stored """

    _entity_provider_list = [ViewedParameterProvider()]
    """
    List of all entity providers that organize data exchange between the viewed parameter and the external database
    storage
    """

    _required_fields = ['descriptor', 'category', 'user']
    """ An entity can't be created until all of these fields will be filled """

    _public_field_description = {
        'index': ReadOnlyField(description="The ordering index"),
        'descriptor': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.ParameterDescriptor",
            description="Descriptor of the parameter to view"
        ),
        'category': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.labjournal_record.Record",
            description="A category which view table is adjusting"
        ),
        'user': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.user.User",
            description="The user that views such a view table",
        )
    }
    """ Describes all public fields within this entity excluding the numerical ID """

    def __setattr__(self, name, value):
        """
        Changes the property

        :param name: name of the property to change
        :param value: new value of such property
        """
        if self.state != 'creating' and name == 'category':
            raise EntityOperationNotPermitted(
                msg="Can't change the 'category' field when the entity has already been created"
            )
        elif self.state != 'creating' and name == 'user':
            raise EntityOperationNotPermitted(
                msg="Can't change the 'user' field when the entity has already been created"
            )
        else:
            super().__setattr__(name, value)
