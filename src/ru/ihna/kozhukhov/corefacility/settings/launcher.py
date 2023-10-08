import sys
import importlib.util
import os
from pathlib import Path
from dotenv import load_dotenv

from django.core.exceptions import ImproperlyConfigured


class ConfigLauncher:
    """
    This is a configuration starter that allows to select a necessary configuration profile and launch the corefacility
    configuration system
    """

    SETTINGS_MODULE = "ru.ihna.kozhukhov.corefacility.settings.config_list"
    """ The module that represents the corefacility configuration system """

    BASE_DIR = None
    """ Directory where all corefacility settings are stored """

    SETTINGS_DIR = None
    """ Directory where Django settings are stored """

    _preliminary_settings_filename = "preliminary.env"
    """ Short name of the preliminary settings file """

    @classmethod
    def find_settings_dir(cls):
        """
        Finds the directory where corefacility settings must be stored.
        IF no such directory exists, the method creates it
        """
        if os.environ.get('COREFACILITY_SETTINGS_DIR') is not None:
            cls.BASE_DIR = Path(os.environ.get('COREFACILITY_SETTINGS_DIR'))
        else:
            if importlib.util.find_spec('posix'):
                cls.BASE_DIR = Path('/etc/corefacility')
            elif sys.platform.startswith('win'):
                raise NotImplementedError('win is not implemented')
            else:
                raise ImproperlyConfigured(
                    "The operating system that you are currently running on is unknown. Hence, in order to run the "
                    "application you must set the COREFACILITY_SETTINGS_DIR environment variable"
                )
        if not os.path.isdir(cls.BASE_DIR):
            os.mkdir(cls.BASE_DIR)
        cls.SETTINGS_DIR = os.path.join(cls.BASE_DIR, 'django-settings')
        if not os.path.isdir(cls.SETTINGS_DIR):
            os.mkdir(cls.SETTINGS_DIR)

    @classmethod
    def get_preliminary_settings_filename(cls):
        """
        Full name of the preliminary settings file.
        The preliminary settings file contains information about a given configuration profile.
        """
        if cls.SETTINGS_DIR is None:
            cls.find_settings_dir()
        return os.path.join(cls.SETTINGS_DIR, cls._preliminary_settings_filename)

    @classmethod
    def select_config_profile(cls):
        """
        Selects a proper configuration profile based on the preliminary settings file.
        """
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", cls.SETTINGS_MODULE)
        preliminary_settings_file = cls.get_preliminary_settings_filename()
        if os.path.isfile(preliminary_settings_file):
            load_dotenv(preliminary_settings_file)
