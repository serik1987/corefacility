from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType
from ru.ihna.kozhukhov.core_application.entity.fields import ManagedEntityField

from .hashtag import Hashtag
from .hashtag_file_manager import HashtagFileManager


class FileHashtag(Hashtag):
    """
    Represents a single file hashtag
    """

    _default_hashtag_type = LabjournalHashtagType.file
    """ Defines the hashtag type based solely on its class """

    _public_field_description = {
        **Hashtag._public_field_description,
        'files': ManagedEntityField(HashtagFileManager, description="Files this hashtag is attached to")
    }
