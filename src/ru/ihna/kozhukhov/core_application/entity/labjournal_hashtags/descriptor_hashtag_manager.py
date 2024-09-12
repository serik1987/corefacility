from ru.ihna.kozhukhov.core_application.models import LabjournalDescriptorHashtag
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType

from .hashtag_manager import HashtagManager


class DescriptorHashtagManager(HashtagManager):
    """
    Allows to add, remove and iterate over all hashtag attachments to the descriptor of custom parameter
    """

    type = LabjournalHashtagType.record
    """ Types of hashtags this manager adds or removes """

    attachment_model = LabjournalDescriptorHashtag
    """ A database where hashtag-to-entity attachments were stored """

    entity_field = 'descriptor_id'
    """ The entity field inside the joint table """

    @property
    def project(self):
        """
        Returns the related project
        """
        return self._entity.category.project
