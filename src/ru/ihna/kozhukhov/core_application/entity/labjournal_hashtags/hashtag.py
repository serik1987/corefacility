from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.entity.fields import EntityField, RelatedEntityField, ReadOnlyField
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityOperationNotPermitted

from .hashtag_set import HashtagSet
from .hashtag_provider import HashtagProvider


class Hashtag(Entity):
    """
    Represents a single hashtag
    """

    _entity_set_class = HashtagSet
    """ Container where all hashtags were stored """

    _entity_provider_list = [HashtagProvider()]
    """ Entity providers are responsible for information exchange between hashtag and the external storage """

    _required_fields = ['description', 'project']
    """ The Hashtag can't be created in the external storage when any of these fields are not assigned """

    _default_hashtag_type = None
    """ Defines the hashtag type based solely on its class """

    _public_field_description = {
        'description': EntityField(str, min_length=1, max_length=64, description="Human-readable hashtag description"),
        'project': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.project.Project",
            description="Project where the hashtag is defined",
        ),
        'type': ReadOnlyField(description="Hashtag type")
    }

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
        if self._default_hashtag_type is None:
            raise EntityOperationNotPermitted(
                msg="Class Hashtag is base class. You can't create instances of this. Use RecordHashtag or FileHashtag"
            )
        else:
            self._type = self._default_hashtag_type
