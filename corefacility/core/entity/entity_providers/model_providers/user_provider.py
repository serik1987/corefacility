from core.models import User
from .model_provider import ModelProvider


class UserProvider(ModelProvider):
    """
    Enables storing user information as Django models
    """

    _entity_model = User
    """ the entity model is a Django model that immediately stores information about the entity """

    _lookup_field = "login"
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _model_fields = ["login", "password_hash", "name", "surname", "email", "phone", "is_locked", "is_superuser",
                     "is_support", "avatar", "unix_group", "home_dir", "activation_code_hash",
                     "activation_code_expiry_date"]
    """
    Defines fields in the entity object that shall be stored as Django model
    """

    _entity_class = "core.entity.user.User"
    """
    Defines the entity class (the string notation)
    """
