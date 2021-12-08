from .entry_point import EntryPoint


class SettingsEntryPoint(EntryPoint):
    """
    Defines the settings entry point

    The settings entry point is used to setup various operating system settings as well as perform
    different hardware health checks
    """

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
