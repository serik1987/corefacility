from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.entity.fields import EntityField, RelatedEntityField
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import \
    EntityOperationNotPermitted, EntityFieldInvalid

from .search_properties_set import SearchPropertiesSet
from .search_properties_provider import SearchPropertiesProvider


class SearchProperties(Entity):
    """
    Responsible for remembering individual settings of the record list filters made by the user.
    """

    _entity_set_class = SearchPropertiesSet
    """ Represents container that contains information about various SearchProperties instances """

    _entity_provider_list = [SearchPropertiesProvider()]
    """ Exchanges information between the SearchProperties instance and the database """

    _required_fields = ['category', 'user', 'properties']
    """ The entity can't be created until any of these fields is not filled """

    _public_field_description = {
        'category': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.labjournal_record.CategoryRecord",
            description="Category which search parameters must be adjusted",
        ),
        'user': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.user.User",
            description="User who adjusted search properties",
        ),
        'properties': EntityField(dict, description="Search properties that have been stored")
    }
    """ Describes all fields and their properties """

    def __setattr__(self, name, value):
        """
        Assigns the value to the field

        :param name: name of the field which value shall be assigned
        :param value: new desired value of the field
        """
        if name == 'category' and self.state != 'creating':
            raise EntityOperationNotPermitted()
        elif name == 'user' and self.state != 'creating':
            raise EntityOperationNotPermitted()
        elif name == 'properties' and not isinstance(value, dict):
            raise EntityFieldInvalid('properties')
        else:
            super().__setattr__(name, value)
