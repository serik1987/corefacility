from .entry_point import EntryPoint
from core.entity.corefacility_module import CorefacilityModule


class SynchronizationsEntryPoint(EntryPoint):
    """
    Allows to attach different kinds of synchronizations and select an appropriate one
    """

    _is_parent_module_root = True
    """ The property is used during the autoloading """

    @classmethod
    def synchronize(cls, **options):
        """
        Chooses a proper synchronization module and provides the synchronization

        :param options: the synchronization options. The synchronization must be successfuly started and successfully
            completed when no options are given
        :return: a dictionary that contains the following fields:
            next_options - None if synchronization shall be completed. If synchronization has not been completed
                this function shall be run repeatedly with the option mentioned in this field.
                Please, note
            details - some information about all completed actions. The information is useful to be printed out.
        """
        from core.synchronizations.exceptions import TeapotError
        entry_point = SynchronizationsEntryPoint()
        for module in entry_point.modules():
            return module.synchronize(**options)
        raise TeapotError()

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

    def synchronize(self, **options):
        """
        Provides an account synchronization

        :param options: the synchronization options. The synchronization must be successfuly started and successfully
            completed when no options are given.
        :return: a dictionary that contains the following fields:
            next_options - None if synchronization shall be completed. If synchronization has not been completed
                this function shall be run repeatedly with the option mentioned in this field.
                Please, note that not all options can be passed back using the URL get parameters
            details - some information about all completed actions. The information is useful to be printed out.
        """
        raise NotImplementedError("To complete the creation of synchronization module please,"
                                  "implement the synchronize method")
