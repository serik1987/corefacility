from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EntityException(Exception):
    pass


class EntityNotFoundException(EntityException):
    def __init__(self):
        super().__init__(_("The requested resource was not found here"))


class EntityDuplicatedException(EntityException):
    def __init__(self):
        super().__init__(_("Unable to create the requested resource because it has already been created"))


class EntityFieldInvalid(EntityException):

    def __init__(self, entity_name):
        super().__init__(_("%s with such values can't exist") % entity_name)


class SupportUserModificationNotAllowed(EntityException):

    def __init__(self):
        super().__init__("You are not allowed to create or modify the 'support' user")


class EntityOperationNotPermitted(EntityException):

    def __init__(self, msg=None):
        if msg is None:
            msg = _("The entity operation is not permitted")
        super().__init__(msg)


class EntityProvidersNotDefined(EntityException):
    def __init__(self):
        super().__init__("To perform create, update or delete operations on the entity you must define "
                         "at least one entity provider")


class EntityFeatureNotSupported(EntityException):
    def __init__(self):
        super().__init__(_("This feature is not supported for current database engine. Use another one"))


class GroupGovernorConstraintFails(EntityException):
    def __init__(self):
        super().__init__(_("The user is a governor of at least one group. "
                           "Its delete will automatically remove these groups and reflect another user rights. "
                           "Are you sure?"))


class ProjectRootGroupConstraintFails(EntityException):
    def __init__(self):
        super().__init__(_("The group is a root group for at least one project. "
                           "Its delete will automatically remove these projects and reflect another user rights. "
                           "Are you sure?"))


class BaseDirIoException(EntityException):
    def __init__(self):
        super().__init__(_("Unable to write to %s directory.") % settings.CORE_PROJECT_BASEDIR)


class LogException(EntityException):
    pass


class NoCurrentLog(LogException):

    def __init__(self):
        super().__init__("No current log was created. Did you include proper 'core' module middleware?")


class CorefacilityModuleException(EntityException):
    pass


class CorefacilityModuleDamagedException(CorefacilityModuleException):

    def __init__(self):
        super().__init__("The corefacility module is damaged: the information containing in the database "
                         "is not the same as information containing in the module class")


class CorefacilityModuleAutoloadFailedException(CorefacilityModuleException):

    def __init__(self, prop, obj):
        super().__init__("Can't retrieve the property %s for the %s because the property was not loaded during the "
                         "autoload" % (prop, obj.get_entity_class_name()))


class EntryPointAutoloadFailedException(CorefacilityModuleException):

    def __init__(self, obj):
        super().__init__("Can't retrieve the autoloadable property for entry point %s because its belonging module "
                         "is not a root module or has not been loaded yet" % obj.get_entity_class_name())


class ModuleUuidNotGuessedException(CorefacilityModuleException):

    def __init__(self, obj):
        super().__init__("When you called use_uuid of the %s module you put wrong UUID as an argument" % repr(obj))


class ModuleConstraintFailedException(CorefacilityModuleException):

    _child_module = None

    def __init__(self, child_module):
        super().__init__("Unable to delete the module because the following module was not deleted: "
                         + repr(child_module))
        self._child_module = child_module

    @property
    def child_module(self):
        """
        The child module that shall be deleted before the parent module is able to be deleted
        """
        return self._child_module


class RootModuleDeleteException(CorefacilityModuleException):

    def __init__(self):
        super().__init__("The root module can't be deleted")


class ModuleNotInstalledException(CorefacilityModuleException):

    def __init__(self):
        super().__init__("Can't setup the module property because the module has not been installed")


class ModuleDeprecatedException(CorefacilityModuleException):

    def __init__(self):
        super().__init__("The module you are trying to use is deprecated. The autoload of an instance you are "
                         "currently using is not possible any more. To solve this problem, please, create another "
                         "module instance using the module constructor and apply autoload again")


class ModuleInstallationException(CorefacilityModuleException):

    def __init__(self, module, msg):
        super().__init__(_("Error during installation of the module") + " '%s': %s" % (repr(module), msg))


class ModuleInstallationStateException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "Can't install the module because its state is not UNINSTALLED")


class ParentModuleNotInstalledException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, _("This module has a parent module that have not been completely installed yet"))


class EntryPointInstallationStateException(CorefacilityModuleException):

    def __init__(self, entry_point):
        super().__init__("Can't install entry point %s because its state is not UNINSTALLED" %
                         entry_point.get_entity_name())


class ModuleInstallationAliasException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "The module alias is not a string or contains illegal symbols")


class ModuleInstallationAliasDuplicatedException(ModuleInstallationException):

    def __init__(self, module, entry_point):
        super().__init__(module, "Module with the same alias has already been installed and attached to the "
                                 "entry point '%s'" % repr(entry_point))


class ModuleInstallationEntryPointException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "The parent entry point for the module is not an instance of the EntryPoint class")


class ParentEntryPointStateException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "The parent entry point of the module can't move to the state LOADED")


class ModuleNameException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "The module name is not a string")


class ModuleHtmlCodeException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "The module HTML code is not valid")


class ModuleApplicationStatusException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "The module 'is_application' property was set incorrectly")


class BelongingModuleIncorrectException(CorefacilityModuleException):

    def __init__(self, entry_point):
        super().__init__("Can't install the entry point '%s' because its belonging module is incorrect "
                         "or can't be autoloaded" % entry_point.get_entity_name())


class EntryPointAliasIncorrectException(CorefacilityModuleException):

    def __init__(self, entry_point):
        super().__init__("Can't install the entry point '%s' because its alias is incorrect"
                         % entry_point.get_entity_name())


class EntryPointDuplicatedException(CorefacilityModuleException):

    def __init__(self, entry_point):
        super().__init__("The entry point '%s' is duplicated" % entry_point.get_entity_name())


class EntryPointNameIncorrectException(CorefacilityModuleException):

    def __init__(self, entry_point):
        super().__init__("Can't install the entry point '%s' because its name is not correct"
                         % entry_point.get_entity_name())


class EntryPointTypeIncorrectException(CorefacilityModuleException):

    def __init__(self, entry_point):
        super().__init__("Can't install the entry point '%s' "
                         "because its type is not a string being equal to either 'lst' or 'sel'"
                         % entry_point.get_entity_name())


class AuthorizationException(CorefacilityModuleException):
    """
    Occurs when the external authorization is finally failed
    """

    __route = None

    def __init__(self, route, message):
        super().__init__(message)
        self.__route = route

    @property
    def route(self):
        return self.__route


class NoLogException(EntityException):
    """
    The exception is originated when no log was attached to the entity.
    """

    def __init__(self, entity):
        super().__init__("No log was attached to the entity {entity}. Please attach the log to the 'log' property "
                         "of the entity (mind, how)".format(entity=repr(entity)))


class PosixException(EntityException):
    """
    Base class for all errors generated by POSIX entity providers and all related objects
    """
    pass


class ConfigurationProfileException(PosixException):
    """
    The exception is thrown if configuration profile doesn't allow to apply the POSIX command launcher
    """

    def __init__(self, profile):
        super().__init__(
            "The configuration profile '{profile}' is not suitable for this action".format(profile=profile)
        )


class DeserializationException(PosixException):
    """
    The exception throws when AutoAdminObject can't be recovered successfully from the PosixRequest model.
    """

    def __init__(self, posix_request, origin):
        super().__init__(
            "Instance AutoAdminObject together with corresponding method can't be properly recovered "
            "from the POSIX request entry with ID = {id} due to {origin}"
            .format(
                id=posix_request.id,
                origin=str(origin),
            )
        )


class SecurityCheckFailedException(PosixException):
    """
    An exception throws when autoadmin can't execute the request due to security reasons.
    """
    pass


class PosixCommandFailedException(PosixException):
    """
    An exception is thrown when this is failed to create, modify or delete the entity becuase some POSIX command
    has been accomplished with error.

    The POSIX command is stated to be completed with error when its corresponding process has finished with non-zero
    status code.
    """

    def __init__(self, posix_command: str, output: str):
        """
        Initializes an exception

        :posix_command: a string representing the POSIX command to execute
        :output: a command output
        """
        super().__init__("Command '%s' executed with the following error: '%s'" % (posix_command, output.strip()))


class RetryCommandAfterException(PosixException):
    """
    The error is thrown when you need to try this operation later.
    """

    def __init__(self):
        super().__init__("Retry after exception: the command shall be executed later.")
