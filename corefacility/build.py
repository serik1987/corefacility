import sys
from django.core.management import ManagementUtility as BaseManagementUtility
from core.management.commands.configure import Command as ConfigurationCommand

COMMAND_NAME = "configure"


class ManagementUtility(BaseManagementUtility):
    """
    The Management utility in the build module doesn't require corefacility's application settings to have already
    been built but allows to execute one command only - the 'configure' command from the 'core' module
    """

    def fetch_command(self, subcommand):
        """
        Tells the ManagementUtility what command we definitely need to execute
        :param subcommand: useless
        :return: the BaseManagementUtility instance
        """
        return ConfigurationCommand()


if __name__ == "__main__":
    arguments = [sys.argv[0], COMMAND_NAME, *sys.argv[1:]]
    utility = ManagementUtility(arguments)
    utility.execute()
