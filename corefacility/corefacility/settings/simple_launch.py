import os
from pathlib import Path
from .base import CorefacilityConfiguration


class SimpleLaunchConfiguration(CorefacilityConfiguration):
    """
    Provides settings for the 'Simple Desktop' configuration profile: the application is deployed on
    a single desktop, the operating system doesn't matter
    """

    # E-mails will not send in desktop configurations
    EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

    # The base directory where all project and user files were located
    CORE_PROJECT_BASEDIR = os.path.join(Path.home(), "My Research")

    # Whether the application can manage UNIX groups
    CORE_MANAGE_UNIX_GROUPS = False

    # Whether the application can manage UNIX users
    CORE_MANAGE_UNIX_USERS = False

    # Whether the application can provide another UNIX administration routines
    CORE_UNIX_ADMINISTRATION = False

    # Whether the application can suggest user to provide a certain administration
    CORE_SUGGEST_ADMINISTRATION = False
