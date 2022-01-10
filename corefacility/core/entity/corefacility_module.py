from django.utils.translation import gettext_lazy as _
from .entity import Entity
from .entity_fields.field_managers.app_permission_manager import AppPermissionManager
from .entity_sets.corefacility_module_set import CorefacilityModuleSet
from .entity_fields import EntityField, ReadOnlyField, ManagedEntityField
from .entity_exceptions import EntityOperationNotPermitted


class CorefacilityModule(Entity):
    """
    Base class for all corefacility modules and applications that defines all necessary information used for
    routing and installation

    Any corefacility module must contain an App class that is:
    a) a subclass of core.entity.CorefacilityModule class
    b) is a singleton
    c) must contains in the package's __init__.py file
    d) the package where the App class contains must be a valid Django applications
    e) all methods marked here as NotImplementedError must be implemented
    """

    _entity_set_class = CorefacilityModuleSet

    _entity_provider_list = []  # TO-DO: declare the proper corefacility module provider

    _required_fields = []

    _public_field_description = {
        "uuid": ReadOnlyField(description="UUID", default="xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx"),
        "parent_entry_point": ReadOnlyField(description="Entry point"),
        "alias": ReadOnlyField(description="Module alias"),
        "name": ReadOnlyField(description="Human-readable module name"),
        "html_code": ReadOnlyField(description="Module HTML code if applicable"),
        "app_class": ReadOnlyField(description="The module application class"),
        "user_settings": EntityField(dict,
                                     description="The user-controlled module settings"),
        "is_application": ReadOnlyField(description="Is module an application"),
        "is_enabled": EntityField(dict, description="Is module enabled"),
        "permissions": ManagedEntityField(AppPermissionManager,
                                          description="Application permissions")
    }

    _module_installation = False

    def get_entity_class_name(self):
        return _(self.get_name())

    def __new__(cls, *args, **kwargs):
        """
        The CorefacilityModule is a singleton which mean that you can create just one module instance

        :param args: Some argument from the superclass constructor
        :param kwargs: Some keyword arguments from the superclass constructor
        """
        if not hasattr(cls, "_instance"):
            cls._instance = super(CorefacilityModule, cls).__new__(cls, *args, **kwargs)
        return getattr(cls, "_instance")

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

    def is_application(self):
        """
        Let's say that the module is "application" if the superuser can provide additional access restrictions to
        the application functionality.

        An example of applications:
        'Optical Imaging', 'ROI' - the superuser can define additional restrictions for using this application, in
        addition to the project restrictions

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

    def create(self):
        """
        You can't create the module, just install it!

        :return: nothing
        """
        if not self._module_installation:
            raise EntityOperationNotPermitted()
        super().create()

    def install(self):
        """
        Adds the module and all its related entry points to the database

        :return: nothing
        """
        raise NotImplementedError("TO-DO: CorefacilityModule.install")

    @property
    def state(self):
        """
        The same as Entity.state but bears in mind that the module can't be 'creating'.

        The module can't be installed or enabled but this simply means that the module
        is not visible from the rest of the app, nothing else.

        :return:
        """
        state = super().state
        if state == "creating":
            state = "saved"
        return state
