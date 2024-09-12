from ru.ihna.kozhukhov.core_application.models import LabjournalHashtagRecord, LabjournalRecord

from .hashtag_entity_manager import HashtagEntityManager


class HashtagRecordManager(HashtagEntityManager):
    """
    Manager list of different records the hashtag is attached to
    """

    _entity_table = LabjournalRecord
    """ A database table where all entities are stored """

    _association_table = LabjournalHashtagRecord
    """ A database tabel where hashtag-to-entity attachments are stored """

    _entity_field = 'record_id'
    """ Name of a column in the association table where entity IDs are stored  """
