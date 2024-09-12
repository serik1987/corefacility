from ru.ihna.kozhukhov.core_application.models import LabjournalFileHashtag
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType

from .hashtag_manager import HashtagManager


class FileHashtagManager(HashtagManager):
    """
    Allows to add, remove and iterate over all hashtag attachments to the file
    """

    type = LabjournalHashtagType.file
    """ Types of hashtags this manager adds or removes """

    attachment_model = LabjournalFileHashtag
    """ A database where hashtag-to-entity attachments were stored """

    entity_field = 'file_id'
    """ The entity field inside the joint table """

    @property
    def project(self):
        """
        Returns the related project
        """
        raise NotImplementedError("TO-DO: FileHashtagManager.project")
