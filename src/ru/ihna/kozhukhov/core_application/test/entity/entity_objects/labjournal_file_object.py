from ru.ihna.kozhukhov.core_application.entity.labjournal_file import File

from .entity_object import EntityObject


class LabjournalFileObject(EntityObject):
    """
    Manipulates the labjournal's File for the testing purpose
    """

    _entity_class = File
    """ The entity class that is used to create the entity itself """

    _default_create_kwargs = {
        'record': None,
        'name': "neurons.dat",
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        'name': "glia.dat"
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """

