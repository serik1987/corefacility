from ....entity.user import User
from .entity_object import EntityObject


class UserObject(EntityObject):
    """
    Allows managing a partucular user entity for the testing purpose
    """

    _entity_class = User
    """ The entity class that is used to create the entity itself """

    _default_create_kwargs = {
        "login": "sergei.kozhukhov",
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        "login": "ivan.ivanov"
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """
