import os
from pathlib import Path
import re
from uuid import UUID

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .entity import Entity
from .entity_sets.corefacility_module_set import CorefacilityModuleSet
from .entity_providers.model_providers.corefacility_module_provider import CorefacilityModuleProvider
from .entity_fields import EntityField, ReadOnlyField, ManagedEntityField
from .entity_fields.field_managers.module_settings_manager import ModuleSettingsManager
from .entity_exceptions import ModuleUuidNotGuessedException, \
    CorefacilityModuleDamagedException, EntityNotFoundException, ModuleInstallationStateException, \
    ModuleInstallationAliasException, ModuleInstallationEntryPointException, ParentEntryPointStateException, \
    ModuleNameException, ModuleHtmlCodeException, ModuleApplicationStatusException, ModuleNotInstalledException, \
    ParentModuleNotInstalledException, ModuleDeprecatedException, EntityOperationNotPermitted


API_URLS_TEMPLATE = """
from django.urls import path, include

urlpatterns = [
    {urlpatterns}
]
"""


class CorefacilityModule(Entity):
    """
    Base class for all corefacility modules and applications that defines all necessary information used for
    routing and installation

    Any corefacility module must contain an App class that is:
    a) a subclass of core.entity.CorefacilityModule class
    b) is a singleton
    c) must contain in the package's __init__.py file
    d) the package where the App class contains must be a valid Django applications
    e) all methods marked here as NotImplementedError must be implemented
    """

    DEFAULT_APP_PERMISSION = "add"

    EP_ROUTES_FILE = "ep_urls/%s.py"

    _entity_set_class = CorefacilityModuleSet

    _entity_provider_list = [CorefacilityModuleProvider()]

    _required_fields = []

    _public_field_description = {
        "uuid": ReadOnlyField(description="UUID", default="xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx"),
        "parent_entry_point": ReadOnlyField(description="Entry point"),
        "alias": ReadOnlyField(description="Module alias"),
        "name": ReadOnlyField(description="Human-readable module name"),
        "html_code": ReadOnlyField(description="Module HTML code if applicable"),
        "app_class": ReadOnlyField(description="The module application class"),
        "user_settings": ManagedEntityField(ModuleSettingsManager,
                                            description="The user-controlled module settings"),
        "is_application": ReadOnlyField(description="Is module an application"),
        "is_enabled": EntityField(bool, description="Is module enabled"),
    }

    _module_installation = False

    _state = None

    _desired_uuid = None

    @classmethod
    def reset(cls):
        """
        Clears all module information loaded from the database.
        This method can probably be used for testing purpose.

        :return: nothing
        """
        if hasattr(cls, "_instance"):
            cls._instance._state = "deprecated"
            delattr(cls, "_instance")

    def __new__(cls, *args, **kwargs):
        """
        The CorefacilityModule is a singleton which mean that you can create just one module instance

        :param args: Some argument from the superclass constructor
        :param kwargs: Some keyword arguments from the superclass constructor
        """
        if not hasattr(cls, "_instance"):
            cls._instance = super(CorefacilityModule, cls).__new__(cls, *args, **kwargs)
        return getattr(cls, "_instance")

    def __init__(self):
        """
        The corefacility module has special init function with no keywords. Any options will be loaded from the
        database automatically or embedded into entity by the module developer.
        """
        if self._public_fields is None:
            self._public_fields = {}
        if self._edited_fields is None:
            self._edited_fields = set()
        if self._state is None:
            self._state = "found"

    @property
    def uuid(self):
        """
        Tries to reveal the module's UUID

        :return: module UUID
        """
        if self.state == "found":
            self._autoload()
        return super().uuid

    @property
    def parent_entry_point(self):
        """
        The entry point which the module belongs to
        """
        return self.get_parent_entry_point()

    @property
    def alias(self):
        """
        The module alias
        """
        return self.get_alias()

    @property
    def name(self):
        """
        The module name
        """
        return self.get_name()

    @property
    def html_code(self):
        """
        HTML code
        """
        return self.get_html_code()

    @property
    def app_class(self):
        """
        The module app class
        """
        return "%s.%s" % (self.__module__, self.__class__.__name__)

    @property
    def user_settings(self):
        """
        Defines the module user settings

        :return: the module user settings
        """
        if self.state == "found":
            self._autoload()
        return super().user_settings

    @property
    def permissions(self):
        """
        Returns the module permission from the user settings
        """
        if not self.is_application:
            raise AttributeError("Permissions are not defined at the application level")
        return self.user_settings.get("permissions", self.DEFAULT_APP_PERMISSION)

    @permissions.setter
    def permissions(self, value):
        """
        Sets the module permissions from the user settings
        """
        from core.models.enums import LevelType
        from core.entity.access_level import AccessLevelSet
        if not self.is_application:
            raise AttributeError("Permissions are not defined at the application level")
        if not isinstance(value, str):
            raise ValueError("The value must be a string")
        level_set = AccessLevelSet()
        level_set.type = LevelType.app_level
        try:
            level_set.get(value)
        except EntityNotFoundException:
            raise ValueError("No such application permission level: '%s'" % value)
        self.user_settings.set("permissions", value)

    @property
    def is_enabled(self):
        """
        Defines whether the module is enabled

        :return: True if the module is enabled, False otherwise
        """
        if self.state == "found":
            self._autoload()
        return super().is_enabled()

    @property
    def state(self):
        """
        Detects the module state

        :return: the module state
        """
        return self._state

    def get_alias(self):
        """
        Returns the application alias.
        The application alias will be used for building and parsing URL routes to get access to
        application API and URL functions.
        The application alias must be unique across all applications connected.

        :return: a small unique string containing letters, digits, underscores and/or dashes
        """
        raise NotImplementedError("get_alias")

    def get_parent_entry_point(self):
        """
        Returns the entry point to which the application is attached. The entry point defines:
        1) How application API routes will be embedded to the overall API route system
        2) Where application widgets will be located inside the 'corefacility' or another child applications

        :return: an instance of the core.entity.EntryPoint class
        """
        raise NotImplementedError("get_parent_entry_point")

    def get_name(self):
        """
        Returns the application name. The application name defines how the application will be visible for
        the other used and for superusers when they adjust your application

        :return: the application name
        """
        raise NotImplementedError("get_name")

    def get_html_code(self):
        """
        Returns the application HTML code. If the application entry point must be represented in the user interface
        in form of some application icon this function shall return an HTML code that must help the web browser
        to show this icon. Use web browser DevTools to know what kind of HTML code you need to represent

        :return: a string containing the application HTML code or None
        """
        raise NotImplementedError("get_html_code")

    @property
    def is_application(self):
        """
        Let's say that the module is "application" if the superuser can provide additional access restrictions to
        the application functionality.

        An example of applications:
        'Optical Imaging', 'ROI' - the use can use the application if and only if the application will be added
        to the project. The application can be added by either superuser or user

        If the module is not an "application" all users will have the same access to the application
        Example of such modules:
        1) authorization modules - all users including unauthorized visitors can use them without any permissions
        2) synchronization modules - system administrators or cron daemons can use them

        :return: True is the module is application, False otherwise
        """
        raise NotImplementedError("is_application")

    def is_enabled_by_default(self):
        """
        Defines whether the module shall be enabled immediately after the installation.

        If the module is enabled, it can be accessed using API and is visible in the UI.
        Otherwise, the module is not accessible using API even for superusers.

        This function provides a default value for this option what will be set immediately after
        installation. Then, supervisors can use API or UI to change the value of this option.

        :return: True if the module is visible by default, False otherwise
        """
        raise NotImplementedError("is_enabled_by_default")

    def get_serializer_class(self):
        """
        Defines the serializer class. The serializer class is used to represent module settings in JSON format
        :return: instance of rest_framework.serializers.Serializer class
        """
        raise NotImplementedError("get_serializer_class")

    def get_entry_points(self):
        """
        You can create your own entry points that allow another corefacility users to create their own
        extensions for your extension and attach such extensions for this entry point

        The level of extensibility is logically unrestricted however we don't recommend you to create
        too deep levels because this can slow processing of the API requests.

        By default, the method returns empty dictionary

        :return: a dictionary where each key is an entry point alias and each value is an EntryPoint instance
        """
        return {}

    def get_entity_class_name(self):
        """
        Returns the module name in the currently set language

        :return: the human-readable module name
        """
        return _(self.get_name())

    def install(self):
        """
        Installs the module by making changes to the module itself, to the file system and to the code of
        a parent module and the core module (if applicable)
        """
        self._install_database()
        self._install_routes()

    def _install_database(self):
        """
        Writes information about the application and all entry points connected to this application
        :return:
        """
        from core import App
        self._check_preinstall_state()
        if not isinstance(self, App):
            parent_entry_point = self._check_parent_entry_point()
            self._check_module_alias(parent_entry_point)
        else:
            self._set_database_property("alias", self.get_alias())
        self._check_module_name()
        self._check_module_html_code()
        self._check_module_is_application()
        self._set_database_property("user_settings", dict())
        self._set_database_property("app_class", self.app_class)
        self._set_database_property("is_enabled", self.is_enabled_by_default())
        with transaction.atomic():
            self._state = "creating"
            self.create()
            self._desired_uuid = self._uuid
            self._autoload()
            for _, entry_point in self.get_entry_points().items():
                entry_point.install(self)

    def _install_routes(self):
        """
        Embeds the module local paths to the global corefacility's path's mapping
        """
        from core import App
        if not isinstance(self, App) and self.parent_entry_point.is_route_exist():
            module_set = CorefacilityModuleSet()
            module_set.entry_point = self.parent_entry_point
            path_list = [
                "path(r'{alias}/', include('{module}.api_urls'))".format(
                    alias=module.alias,
                    module=module.app_class.split(".App", 1)[0]
                )
                for module in module_set
            ]
            import inspect
            ep_file = inspect.getfile(type(self.parent_entry_point))
            file_name = str(Path(ep_file).parent.parent / self.EP_ROUTES_FILE) % self.parent_entry_point.alias
            file_content = API_URLS_TEMPLATE.format(urlpatterns=",\n".join(path_list))
            with open(file_name, "w") as routes_file:
                routes_file.write(file_content)

    def _check_preinstall_state(self):
        """
        Module installation step 1: ensure that the module has not been installed

        :return: nothing
        """
        entry_point = self.get_parent_entry_point()
        if entry_point is not None:
            ep_id = entry_point.id
            if entry_point.state == "uninstalled":
                raise ParentModuleNotInstalledException(self)
        self._autoload()
        if self.state != "uninstalled":
            raise ModuleInstallationStateException(self)

    def _check_parent_entry_point(self):
        """
        Module installation step 2: parent entry point validation
        has already been installed

        :return: the parent entry point
        """
        from core.entity.entry_points.entry_point import EntryPoint
        parent_entry_point = self.get_parent_entry_point()
        if not isinstance(parent_entry_point, EntryPoint):
            raise ModuleInstallationEntryPointException(self)
        parent_entry_point_id = parent_entry_point.id
        if parent_entry_point.state != "loaded":
            raise ParentEntryPointStateException(self)
        self._set_database_property("parent_entry_point", parent_entry_point)
        return parent_entry_point

    def _check_module_alias(self, parent_entry_point):
        """
        Module installation step 3: module alias validation

        :param parent_entry_point: the parent entry point revealed during the step 2
        :return: nothing
        """
        module_alias = self.get_alias()
        if not isinstance(module_alias, str) or re.match(r'^[\w\-]+$', module_alias) is None:
            raise ModuleInstallationAliasException(self)
        module_set = CorefacilityModuleSet()
        module_set.entry_point = parent_entry_point
        try:
            module_set.get(module_alias)
        except EntityNotFoundException:
            pass
        self._set_database_property("alias", module_alias)

    def _check_module_name(self):
        """
        Module installation step 4: module name validation

        :return: nothing
        """
        module_name = self.get_name()
        if not isinstance(module_name, str):
            raise ModuleNameException(self)
        self._set_database_property("name", module_name)

    def _check_module_html_code(self):
        """
        Module installation step 5: HTML code validation

        :return: nothing
        """
        html_code = self.get_html_code()
        if html_code is not None and not isinstance(html_code, str):
            raise ModuleHtmlCodeException(self)
        self._set_database_property("html_code", html_code)

    def _check_module_is_application(self):
        """
        Module installation step 6: is_application property validation

        :return: nothing
        """
        is_application = self.is_application
        if not isinstance(is_application, bool):
            raise ModuleApplicationStatusException(self)
        self._set_database_property("is_application", is_application)

    def _set_database_property(self, name, value):
        """
        Module installation sub-routine: sets the property to its default value. This sub-routine is important
        if we want this value to be saved to the database

        :param name: the property name
        :param value: the property value
        :return: nothing
        """
        setattr(self, '_' + name, value)
        self.notify_field_changed(name)

    def use_uuid(self, uuid):
        """
        In order to reveal the module UUID, user_settings and is_enabled properties the module shall be
        autoloaded from the database. In order to autoload the module you shall use this method to set up
        module's UUID as cue. Such a cue is saved in the module's api_urls moudule.

        If the cue is valid UUID value these properties will be autoloaded successfully. Otherwise an exception will
        be generated.

        :param uuid: the UUID cue to setup.
        :return: nothing
        """
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        self._desired_uuid = uuid

    def delete(self):
        """
        Deletes the entity from the database and all its auxiliary sources

        The entity can't be deleted when it still 'creating'.

        NOTE. Please, delete the module variable as well, like here:
        module.delete()
        del module

        :return: nothing
        """
        if self.state == "found":
            self._autoload()
        if self.state == "deprecated":
            raise ModuleDeprecatedException()
        if self.state == "uninstalled":
            raise EntityOperationNotPermitted()
        with transaction.atomic():
            for entry_point_alias, entry_point in self.get_entry_points().items():
                entry_point.delete()
            super().delete()
            self._state = "deleted"
            self.__class__.reset()

    def update(self):
        """
        Updates the entity to the database and all its auxiliary sources

        The update is not possible when the entity state is not 'changed'

        :return: nothing
        """
        super().update()
        self._state = "saved"

    def notify_field_changed(self, field_name):
        """
        When EntityValueManager changes some entity fields it must call this method to notify this entity
        that the field has been change.

        If the EntityValueManager doesn't do this, the entity state will not be considered as 'changed' which
        results to EntityOperationNotPermitted exception.

        :param field_name: the field name that has been changed by the field manager
        :return: nothing
        """
        super().notify_field_changed(field_name)
        self._state = "changed"

    def __repr__(self):
        """
        Returns a short entity representation used for debugging purpose only

        :return: a short entity representation
        """
        s = self.get_entity_class_name()
        if self._uuid is not None:
            s += " (%s) " % str(self._uuid)
        else:
            s += " (UUID is unknown) "
        s += self.state.upper()
        return s

    def _autoload(self):
        """
        Autoloads the module. Call use_uuid in order to autoload the module successfully.

        Also, is the module's entry point has already been loaded there is no necessity to autoload the module.

        :return: nothing
        """
        module_set = CorefacilityModuleSet()
        if self._state == "deprecated":
            raise ModuleDeprecatedException()
        try:
            if self._desired_uuid is not None:
                another_module = module_set.get(self._desired_uuid)
                if another_module is not self:
                    raise ModuleUuidNotGuessedException(self)
            else:
                entry_point = self.get_parent_entry_point()
                if entry_point is None:
                    module_set.is_root_module = True
                else:
                    module_set.entry_point = entry_point
                another_module = module_set.get(self.get_alias())
                if another_module is not self:
                    raise CorefacilityModuleDamagedException()
        except EntityNotFoundException:
            self._state = "uninstalled"

    def __setattr__(self, name, value):
        """
        Sets the public field property.

        If the property name is not within the public or private fields the function throws AttributeError

        :param name: public, protected or private field name
        :param value: the field value to set
        :return: nothing
        """
        if name in self._public_field_description:
            description = self._public_field_description[name]
            description.correct(value)
            if self.state == "found":
                self._autoload()
            if self.state == "uninstalled":
                raise ModuleNotInstalledException()
            super().__setattr__(name, value)
            self._state = "changed"
        else:
            super().__setattr__(name, value)

    def __eq__(self, other):
        """
        Compares two corefacility modules, just for the debugging purpose

        :param other: another module
        :return: True if two modules are equal, False otherwise
        """
        if not isinstance(other, CorefacilityModule):
            return False
        return self.uuid == other.uuid
