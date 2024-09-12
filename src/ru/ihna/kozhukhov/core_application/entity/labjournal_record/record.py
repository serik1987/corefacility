import re
from datetime import datetime

from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.entity.fields import \
    RelatedEntityField, ReadOnlyField, EntityAliasField, DateTimeField, BooleanField, EntityField, ManagedEntityField
from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import RecordHashtagManager

from .record_set import RecordSet
from .record_provider import RecordProvider
from .category_startdate_provider import CategoryStartdateProvider
from .record_check_provider import RecordCheckProvider


class Record(Entity):
    """
    This is the base class for all labjournal records
    """

    _entity_set_class = RecordSet
    """ All labjournal records belong to the RecordSet container """

    _entity_provider_list = [
        RecordProvider(),
        CategoryStartdateProvider(),
        RecordCheckProvider(),
    ]
    """
    Each entity provider is responsible for interaction between the labjournal Record and
    a single database table
    """

    _default_record_type = None
    """ Reflects a particular subclass of the labjournal record """

    _previous_parent_category = None
    """ The previous parent category which datetime is required to be updated when the entity was updated itself """

    _public_field_description = {

        'parent_category': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record.CategoryRecord",
            description="Parent category",
        ),

        'project': ReadOnlyField(description="Related project"),

        'level': ReadOnlyField(default=0, description="Depth level for a given record"),

        'alias': EntityAliasField(
            max_length=64,
            pattern=re.compile(r'^[A-Za-z0-9\-_]+$')
        ),

        'path': ReadOnlyField(default=None, description="Full path to the laboratory record"),

        'datetime': DateTimeField(datetime, description="Date and time of the record start"),

        'relative_time': ReadOnlyField(description="Time of the record start, relatively to the parent category"),

        'user': RelatedEntityField(
            "ru.ihna.kozhukhov.core_application.entity.user.User",
            description="Defines the user context (for store/retrieval individual user settings)",
        ),

        'checked': BooleanField(default=False, description="The user has checked the field"),

        'type': ReadOnlyField("The record type (D for data, S for service, C for category)"),

        'hashtags': ManagedEntityField(RecordHashtagManager, description="Attached hashtags"),

        'comments': EntityField(str, max_length=16_384, description="Extra record")
    }
    """
    Describes all public fields within the model layer
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
        if self._default_record_type is None:
            raise NotImplementedError("This class is purely abstract: use one of its descendants")
        else:
            self._public_fields['type'] = self._default_record_type

    @classmethod
    def get_entity_class_name(cls):
        """
        Returns a human-readable entity class name

        :return: a human-readable entity class name
        """
        return cls._default_record_type.label

    @property
    def is_root_record(self):
        """
        Returns True if record is root record
        """
        return False

    def __setattr__(self, name, value):
        """
        Sets the public field property.

        If the property name is not within the public or private fields the function throws AttributeError

        :param name: public, protected or private field name
        :param value: the field value to set
        :return: nothing
        """
        super().__setattr__(name, value)
        if name == 'parent_category':
            self._public_fields.update({
                'project': value.project,
                'level': value.level + 1,
            })
            self._edited_fields.add('project')
            self._edited_fields.add('level')
        if self._user is None and name in ('checked',):
            raise RuntimeError("The field '%s' is not accessible outside the user context" % name)
