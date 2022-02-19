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
