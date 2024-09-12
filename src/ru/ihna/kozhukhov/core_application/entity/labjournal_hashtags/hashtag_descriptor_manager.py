from ru.ihna.kozhukhov.core_application.models import LabjournalDescriptorHashtag, LabjournalParameterDescriptor

from .hashtag_entity_manager import HashtagEntityManager


class HashtagDescriptorManager(HashtagEntityManager):
    """
    Manages list of different descriptors the hashtag is attached to
    """

    _entity_table = LabjournalParameterDescriptor
    """ A database table where all entities are stored """

    _association_table = LabjournalDescriptorHashtag
    """ A database tabel where hashtag-to-entity attachments are stored """

    _entity_field = 'descriptor_id'
    """ Name of a column in the association table where entity IDs are stored  """
