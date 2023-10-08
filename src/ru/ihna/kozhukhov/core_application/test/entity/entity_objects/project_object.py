from ....entity.project import Project
from .entity_object import EntityObject


class ProjectObject(EntityObject):
    """
    Facilitates testing of projects and makes the project code more attractive
    """

    _default_create_kwargs = {
        "alias": "vasomotor-oscillations",
        "name": "Вазомоторные колебания",
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        "alias": "ontogenesis",
        "name": "Отногенез",
        "description": "Исследование критических периодов онтогенеза в первичной зрительной коре",
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """

    _entity_class = Project
    """ The entity class that is used to create the entity itself """
