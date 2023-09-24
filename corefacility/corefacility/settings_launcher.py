import os
from pathlib import Path
from dotenv import load_dotenv

SETTINGS_MODULE = "corefacility.settings"
BASE_DIR = Path(__file__).parent.parent.parent
SETTINGS_DIR = os.path.join(BASE_DIR, "settings")
PRELIMINARY_SETTINGS_FILENAME = os.path.join(SETTINGS_DIR, "preliminary.env")


def select_config_profile():
    """
    Tries to select certain configuration profile from preliminary.env file

    :return: Nothing
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    try:
        if not os.path.isfile(PRELIMINARY_SETTINGS_FILENAME):
            raise OSError("Preliminary defaults not found")
        load_dotenv(PRELIMINARY_SETTINGS_FILENAME)
    except OSError:
        print("Configuration profile is not found here: %s\n"
              "Hence, we will use the default configuration profile: SimpleLaunchConfiguration\n"
              "This is a critical error. To fix this please, follow the installation instructions\n"
              % PRELIMINARY_SETTINGS_FILENAME)
        os.environ.setdefault("DJANGO_CONFIGURATION", "SimpleLaunchConfiguration")
