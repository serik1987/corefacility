from core.entity.group import Group
from core.tests.entity.entity_objects.entity_object import EntityObject


class GroupObject(EntityObject):
    """
    Allows to manipulate user group during the user group testing
    """

    _default_create_kwargs = {
        "name": "Группа оптического картирования"
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        "name": "Вазомоторные колебания"
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """

    _entity_class = Group
    """ The entity inside the project """
