from ru.ihna.kozhukhov.core_application.models import LabjournalFileHashtag, LabjournalFile

from .hashtag_entity_manager import HashtagEntityManager


class HashtagFileManager(HashtagEntityManager):
    """
    Manages list of different files this hashtag is attached to
    """
    _entity_table = LabjournalFile
    """ A database table where all entities are stored """

    _association_table = LabjournalFileHashtag
    """ A database tabel where hashtag-to-entity attachments are stored """

    _entity_field = 'file_id'
    """ Name of a column in the association table where entity IDs are stored  """

    _project_lookup_field = 'record__project_id'
    """ A column inside the database that contains project IDs """
