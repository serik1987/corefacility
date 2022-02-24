from core.entity.project_application import ProjectApplication
from imaging import App as ImagingApp

from .entity_object import EntityObject


class ProjectApplicationObject(EntityObject):
    """
    Facilitates access to the ProjectApplication entity for testing purpose.
    """

    _entity_class = ProjectApplication
    """ The entity class that is used to create the entity itself """

    _default_create_kwargs = {
        "application": ImagingApp(),
        "is_enabled": True,
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        "is_enabled": False
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """
