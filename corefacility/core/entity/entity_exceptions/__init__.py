from django.utils.translation import gettext as _


class EntityException(Exception):
    """
    The base exception that marks all troubles happened on the level entity
    """
    pass


class EntityNotFoundException(EntityException):
    def __init__(self):
        super().__init__(_("The requested resource was not found here"))


class EntityFieldInvalid(EntityException):

    def __init__(self, entity_name):
        super().__init__(_("%s with such values can't exist") % entity_name)
