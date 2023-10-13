import sys
import traceback

from colorama import init
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ru.ihna.kozhukhov.core_application.management.utility import ManagementUtility
from ru.ihna.kozhukhov.corefacility.settings.launcher import ConfigLauncher

init()


def main():
    try:
        ConfigLauncher.select_config_profile()
        try:
            from configurations import management
        except ImproperlyConfigured as error:
            print("WARNING: The configuration has not been properly set. All 'corefacility' features are reduced.",
                  file=sys.stderr)
            print("REASON: {0}".format(error), file=sys.stderr)
            if "--traceback" in sys.argv:
                traceback.print_exception(error)
        if len(sys.argv) > 1 and sys.argv[1] not in ('configure', 'help'):
            # 'configure' is the only command that wants bad configuration
            # noinspection PyStatementEffect
            settings.INSTALLED_APPS
        utility = ManagementUtility(sys.argv)
        utility.execute()
    except Exception as err:
        if "--traceback" in sys.argv:
            raise
        else:
            print("FATAL ERROR: ", str(err), file=sys.stderr)
            sys.exit(-1)
