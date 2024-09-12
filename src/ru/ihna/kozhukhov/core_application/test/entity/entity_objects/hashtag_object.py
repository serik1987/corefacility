from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import RecordHashtag
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType

from .entity_object import EntityObject


class HashtagObject(EntityObject):
    """
    Manipulates the Hashtag class for testing purpose
    """

    _entity_class = RecordHashtag
    """ Class of the object to test """

    _default_create_kwargs = {
        'description': "решётка",
        'project': None,
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        'description': "прямоугольная решётка"
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """

    def reload_entity(self):
        """
        Loads the recently saved entity from the database

        :return: nothing
        """
        if self._id is None:
            raise RuntimeError("EntityObject.reload_entity: can't reload the entity that is recently saved")
        entity_set = self._entity.get_entity_set_class()()
        entity_set.project = self._default_create_kwargs['project']
        entity_set.type = LabjournalHashtagType.record
        self._entity = entity_set.get(self._id)
