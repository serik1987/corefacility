from .entry_point import EntryPoint
from core.entity.corefacility_module import CorefacilityModule


class SynchronizationsEntryPoint(EntryPoint):
    """
    Allows to attach different kinds of synchronizations and select an appropriate one
    """

    _is_parent_module_root = True
    """ The property is used during the autoloading """

    def get_alias(self):
        """
        Alias for this entry point is also the same: synchronizations

        :return: the entry point alias
        """
        return "synchronizations"

    def get_name(self):
        """
        Returns the public entry point name to be used in the UI

        :return: the entry point name
        """
        return "Account synchronization"

    def get_type(self):
        return "sel"


class SynchronizationModule(CorefacilityModule):
    """
    All modules attached to this entry point must be derived this class.

    This allows more tight connection between the core functionality and particular module
    """

    def get_parent_entry_point(self):
        return SynchronizationsEntryPoint()

    def get_html_code(self):
        """
        Any synchronization process is started either from the user settings or by CRON.
        No other synchronization way is required. Hence, no additional icons shall be provided

        :return: None
        """
        return None

    @property
    def is_application(self):
        """
        This is not application because its access permissions can't be manually adjusted:
        supervisors only have access to this application

        :return: False
        """
        return False

    def is_enabled_by_default(self):
        """
        By default, the module is disabled. The superuser needs to properly adjusts it.

        :return: False
        """
        return False
