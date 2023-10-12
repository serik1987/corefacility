import sys
import traceback

from django.core.management import ManagementUtility
from django.core.exceptions import ImproperlyConfigured
from colorama import init
init()

from ru.ihna.kozhukhov.corefacility.settings.launcher import ConfigLauncher
from ru.ihna.kozhukhov.core_application.management.commands.configure import Command as ConfigurationCommand


class ConfigurationUtility(ManagementUtility):
    """
    The configuration utility is an extension of the ManagementUtility that is responsible for the CLI configuration
    at the very first start of the application when the list of all applications are not properly setup.

    In this case, the utility recognizes just one command - 'configure' and all Django builtin commands.
    """

    def fetch_command(self, subcommand):
        """
        Try to fetch the given subcommand, printing a message with the
        appropriate command called from the command line (usually
        "django-admin" or "manage.py") if it can't be found.
        """
        if subcommand == "configure":
            return ConfigurationCommand()
        else:
            print("Fatal error: "
                  "The corefacility was not configured, so only 'corefacility configure' command can be run",
                  file=sys.stderr)
            sys.exit(-1)


def main():
    config_profile_selected = False
    try:
        try:
            ConfigLauncher.select_config_profile()
            config_profile_selected = True
        except PermissionError:
            print("Error: The very first launch of the corefacility must be called either under root or "
                  "with 'COREFACILITY_SETTINGS_DIR' environment variable properly installed.", file=sys.stderr)
        try:
            from configurations.management import execute_from_command_line
            from django.conf import settings
            # noinspection PyStatementEffect
            settings.CONFIGURATION
            execute_from_command_line(sys.argv)
        except ImproperlyConfigured as err:
            print("The corefacility was not configured due to the following error:\n", err)
            if "--traceback" in sys.argv:
                traceback.print_exception(err)
            if config_profile_selected:
                utility = ConfigurationUtility(sys.argv)
                utility.execute()
            else:
                print("Fatal error: The error above is crucial (fatal)", file=sys.stderr)
                sys.exit(1)
    except Exception as error:
        if "--traceback" in sys.argv:
            raise
        else:
            print("Fatal error: " + str(error), file=sys.stderr)
            sys.exit(1)
