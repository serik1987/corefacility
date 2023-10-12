import os
from pathlib import Path

from configurations import values

from ru.ihna.kozhukhov.corefacility.settings.config_list.base import CorefacilityConfiguration


class VirtualServerConfiguration(CorefacilityConfiguration):
    """
    Provides settings for the 'Virtual Server' configuration profile: the application is deployed on the Linux
    server and is unable to provide its administration
    """

    # The base directory where all project and user files were located
    CORE_PROJECT_BASEDIR = values.Value(os.path.join(Path.home(), ".research"))

    # E-mail support
    EMAIL_SUPPORT = True

    # Whether the application can manage UNIX groups
    CORE_MANAGE_UNIX_GROUPS = False

    # Whether the application can manage UNIX users
    CORE_MANAGE_UNIX_USERS = False

    # Whether the application can provide another UNIX administration routines
    CORE_UNIX_ADMINISTRATION = False

    # Whether the application can suggest user to provide a certain administration
    CORE_SUGGEST_ADMINISTRATION = False
