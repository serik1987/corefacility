from core.models import AccessLevel as AccessLevelModel

from .model_provider import ModelProvider


class AccessLevelProvider(ModelProvider):

    _entity_model = AccessLevelModel
    """ the entity model is a Django model that immediately stores information about the entity """

    _lookup_field = "id"
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _model_fields = ["type", "alias", "name"]
    """
    Defines fields in the entity object that shall be stored as Django model. The model fields will be applied
    during object create and update operations
    """

    _entity_class = "core.entity.access_level.AccessLevel"
    """
    Defines the entity class (the string notation)
    """
