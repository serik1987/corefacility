from ru.ihna.kozhukhov.core_application.entity.fields import ManagedEntityField
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType

from .hashtag import Hashtag
from .hashtag_record_manager import HashtagRecordManager
from .hashtag_descriptor_manager import HashtagDescriptorManager


class RecordHashtag(Hashtag):
    """
    Represents a single record hashtag
    """

    _default_hashtag_type = LabjournalHashtagType.record
    """ Defines the hashtag type based solely on its class """

    _public_field_description = {
        **Hashtag._public_field_description,
        'records': ManagedEntityField(HashtagRecordManager, description="Records the hashtag is attached to"),
        'descriptors': \
            ManagedEntityField(HashtagDescriptorManager, description="Descriptors the hashtag is attached to"),
    }
