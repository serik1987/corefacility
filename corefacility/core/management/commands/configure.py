import os
from pathlib import Path
import shutil
from django.core.management import BaseCommand
from django.core.management.utils import get_random_secret_key
from corefacility.settings_launcher import SETTINGS_DIR


class Command(BaseCommand):
    """
    Defines a command that loads all configuration defaults
    """

    DEFAULTS = os.path.join(Path(SETTINGS_DIR).parent, "corefacility/corefacility/settings/defaults")

    def handle(self, *args, **options):
        """
        Loads all configuration defaults

        :param args: arguments passed by the user
        :param options: options
        :return: nothing
        """
        print("This command will erase all configuration settings made by you and restore defaults")
        self._remove_old_files()
        self._copy_configuration_defaults()
        self._generate_secret_key()

    def _remove_old_files(self):
        for filename in os.listdir(SETTINGS_DIR):
            fullname = os.path.join(SETTINGS_DIR, filename)
            os.remove(fullname)
            print("The following configuration was removed: " + fullname)

    def _copy_configuration_defaults(self):
        for filename in os.listdir(self.DEFAULTS):
            fullname = os.path.join(self.DEFAULTS, filename)
            if os.path.isfile(fullname) and fullname.endswith(".env"):
                dst = os.path.join(SETTINGS_DIR, filename)
                shutil.copyfile(fullname, dst)
                print("Copying %s -> %s" % (fullname, dst))

    def _generate_secret_key(self):
        secret = get_random_secret_key()
        secret_property = "DJANGO_SECRET_KEY=%s" % secret
        secret_file = os.path.join(SETTINGS_DIR, "secret.env")
        with open(secret_file, "w") as f:
            f.write(secret_property)
        print("Generating the following file with secret key: " + secret_file)
