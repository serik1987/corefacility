from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.entity.entity_sets.entity_set import EntitySet
from ru.ihna.kozhukhov.core_application.entity.project import Project
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType

from .hashtag_reader import HashtagReader


class HashtagSet(EntitySet):
    """
    Represents a container that contains different hashtag sets
    """

    _entity_name = _("Hashtag")
    """ Human-readable entity name """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags.Hashtag"
    """ Hashtags that are created by means of this entity set """

    _entity_reader_class = HashtagReader
    """
    Entity readers are responsible for reading the hashtag information from the external storage and making
    different Hashtag instances based on such information
    """

    _entity_filter_list = {
        'description': (str, lambda description: len(description) > 0),
        'project': (Project, None),
        'type': (LabjournalHashtagType, None),
    }
    """ Different filtration criteria """

    _alias_kwarg = 'description'
    """ Hashtag description field that is used as alias in the get() method """
