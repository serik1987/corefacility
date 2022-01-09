from django.utils.translation import gettext_lazy as _

from core.entity.access_level import AccessLevel

from .entity_object import EntityObject


class AccessLevelObject(EntityObject):
    """
    Facilitates testing the access levels
    """

    _entity_class = AccessLevel
    """ The entity class that is used to create the entity itself """

    _default_create_kwargs = {
        "alias": "sim",
        "name": "Launching simulation"
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        "name": "Running simulation"
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """
