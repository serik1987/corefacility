import os
from pathlib import Path
from dotenv import load_dotenv

SETTINGS_MODULE = "corefacility.settings"
PRELIMINARY_DEFAULTS_FILENAME = "settings/defaults/preliminary.env"


def select_config_profile():
    """
    Tries to select certain configuration profile from preliminary.env file

    :return: Nothing
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    try:
        base_dir = Path(__file__).parent
        preliminary_defaults_fullname = os.path.join(base_dir, PRELIMINARY_DEFAULTS_FILENAME)
        if not os.path.isfile(preliminary_defaults_fullname):
            raise OSError("Preliminary defaults not found")
        load_dotenv(preliminary_defaults_fullname)
    except OSError:
        print("WARNING Unable to find %s\n"
              "This is OK if you set DJANGO_CONFIGURATION and DJANGO_SETTINGS environment\n"
              "variables before running this file\n"
              "Otherwise this will generate error" % PRELIMINARY_DEFAULTS_FILENAME)
