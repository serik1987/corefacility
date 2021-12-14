from django.utils.translation import gettext_lazy as _


class EntityException(Exception):
    pass


class EntityNotFoundException(EntityException):
    def __init__(self):
        super().__init__(_("The requested resource was not found here"))


class EntityFieldInvalid(EntityException):

    def __init__(self, entity_name):
        super().__init__(_("%s with such values can't exist") % entity_name)


class EntityOperationNotPermitted(EntityException):

    def __init__(self):
        super().__init__(_("The entity operation is not permitted"))


class EntityProvidersNotDefined(EntityException):
    def __init__(self):
        super().__init__("To perform create, update or delete operations on the entity you must define "
                         "at least one entity provider")


class LogException(EntityException):
    pass


class NoCurrentLog(LogException):

    def __init__(self):
        super().__init__("No current log was created. Did you include proper 'core' module middleware?")
