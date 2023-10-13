import pkgutil
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.core.management import ManagementUtility as BaseManagementUtility


class ManagementUtility(BaseManagementUtility):
    """
    This is an extension of standard Django management utility that has the following two improvements:

    (1) the utility can find commands within the 'ru.ihna.kozhukhov.core_application' even when the system has not
        been properly configured (that is, no application list was defined).
    (2) the utility can support commands inside the 'ru.ihna.kozhukhov.core_application' application even when they
        are packages, not standalone modules.
    (3) the utility can run several commands as child processes and manages these processes (e.g., distribute signals
        among them and so on).
    """

    def main_help_text(self, commands_only=False):
        """Return the script's main help text, as a string."""
        help_text = super().main_help_text(commands_only)
        if isinstance(self.settings_exception, ImproperlyConfigured):
            help_text += ("\nPlease note, that if the settings has not been properly configured, you need to run "
                          "'corefacility configure' and then configure the settings properly")
        return help_text

    def fetch_command(self, subcommand):
        """
        Try to fetch the given subcommand, printing a message with the
        appropriate command called from the command line (usually
        "django-admin" or "manage.py") if it can't be found.
        """
        command = self.fetch_core_command(subcommand)
        if command is None:
            command = super().fetch_command(subcommand)
        return command

    @staticmethod
    def fetch_core_command(subcommand):
        """
        Try to fetch the given subcommand within the 'core_application' application.
        This method doesn't require any settings to be properly configured but it allows to fetch commands only
        within one single application
        """
        from . import commands
        available_commands = [
            command.name
            for command in pkgutil.iter_modules(commands.__path__)
            if not command.name.startswith("_")
        ]
        if subcommand in available_commands:
            command_module = import_module("%s.%s" % (commands.__name__, subcommand))
            return command_module.Command()
        else:
            return None
