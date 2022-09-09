from .entry_point import EntryPoint
from ..corefacility_module import CorefacilityModule


class SettingsEntryPoint(EntryPoint):
    """
    Defines the settings entry point

    The settings entry point is used to setup various operating system settings as well as perform
    different hardware health checks
    """
    _is_parent_module_root = True
    """ The property is used during the autoloading """

    def get_alias(self):
        """
        The entry point is accessible from the core module by 'settings' alias

        :return: the entry point alias
        """
        return "settings"

    def get_name(self):
        """
        Returns the settings name

        :return: the settings name
        """
        return "Other settings"

    def get_type(self):
        return "lst"

    def is_route_exist(self):
        """
        Defines whether the entry point participates in the API conjunction.
        IF the entry point participates in the API conjunction all modules attached to it must have api_urls
        python's module in their root directory and corefacility's automatic configuration system will organize
        URL paths through this entry point. Also, such paths will be updated during migration of any child application
        :return: True if the entry point participates in the API conjunction, False otherwise
        """
        return False


class SettingsModule(CorefacilityModule):
    """
    Defines the settings module.

    The settings module provides basic routines for server testing and launching basic server routines.
    """

    def get_parent_entry_point(self):
        """
        Informs the corefacility about the base entry point

        :return: always SettingsEntryPoint instance
        """
        return SettingsEntryPoint()

    @property
    def is_application(self):
        """
        Returns whether the module is application (i.e., whether its access rules can be adjusted)

        :return: always False
        """
        return False

    def is_enabled_by_default(self):
        """
        Checks whether the application shall be enabled by default

        :return: always True: just install and use the settings module, no additional security holes will be happened.
        """
        return True
