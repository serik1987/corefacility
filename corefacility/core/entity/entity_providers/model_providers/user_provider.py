from core.models import User, GroupUser
from .model_provider import ModelProvider
from ...entity import Entity
from ...entity_exceptions import GroupGovernorConstraintFails


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

    def delete_entity(self, user):
        """
        Tries to delete the user from the database

        :param user: the user to delete
        :return: nothing
        """
        if GroupUser.objects.filter(user_id=user.id, is_governor=True).count() > 0:
            raise GroupGovernorConstraintFails()
        super().delete_entity(user)
