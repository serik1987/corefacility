import os
from pathlib import Path

from .base import CorefacilityConfiguration


class ExtendedLaunchConfiguration(CorefacilityConfiguration):
    """
    Provides settings for the 'Linux Desktop' profile: the application is deployed on the Linux desktop PC
    and can configure operating system
    """

    # E-mails will not send in desktop configurations
    EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

    # The base directory where all project and user files were located
    CORE_PROJECT_BASEDIR = os.path.join(Path.home(), ".research")

    # Whether the application can manage UNIX groups
    CORE_MANAGE_UNIX_GROUPS = False

    # Whether the application can manage UNIX users
    CORE_MANAGE_UNIX_USERS = False

    # Whether the application can provide another UNIX administration routines
    CORE_UNIX_ADMINISTRATION = True

    # Whether the application can suggest user to provide a certain administration
    CORE_SUGGEST_ADMINISTRATION = False

    @classmethod
    def check_config_possibility(cls):
        """
        Checks whether the configuration profile is applicable. If not throws MalformedConfiguration

        :return: Nothing.
        """
        cls.check_posix()
        cls.check_sudo()
