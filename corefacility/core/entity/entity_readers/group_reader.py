from core.entity.entity_providers.model_providers.group_provider import GroupProvider
from core.models import Group as GroupModel

from core.entity.entity_readers.model_reader import ModelReader


class GroupReader(ModelReader):
    """
    Picks up scientific group data from the database
    """

    _entity_model_class = GroupModel
    """ A link to the Django model layer """

    _entity_provider = GroupProvider()
    """ The group provider will be used to wrap groups """
