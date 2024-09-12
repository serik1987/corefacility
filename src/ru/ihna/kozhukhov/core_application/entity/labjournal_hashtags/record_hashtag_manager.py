from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType
from ru.ihna.kozhukhov.core_application.models import LabjournalHashtagRecord

from .hashtag_manager import HashtagManager


class RecordHashtagManager(HashtagManager):
    """
    Allows to add, remove and iterate over all hashtag attachments to the laboratory journal records
    """

    type = LabjournalHashtagType.record
    """ Types of hashtags this manager adds or removes """

    attachment_model = LabjournalHashtagRecord
    """ A database where hashtag-to-entity attachments were stored """

    entity_field = 'record_id'
    """ The entity field inside the joint table """

    @property
    def project(self):
        """
        Returns the related project
        """
        return self._entity.project
