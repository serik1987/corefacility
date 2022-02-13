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
                         "autoload" % (prop, repr(obj)))


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


class ModuleInstallationException(CorefacilityModuleException):

    def __init__(self, module, msg):
        super().__init__("Error during installation of the module '%s': %s" % (repr(module), msg))


class ModuleInstallationStateException(ModuleInstallationException):

    def __init__(self, module):
        super().__init__(module, "Can't install the module because its state is not UNINSTALLED")


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


class EntryPointDuplicatedException(ModuleInstallationException):

    def __init__(self, module, entry_point):
        super().__init__(module, "The entry point '%s' has been duplicated" % repr(entry_point))
