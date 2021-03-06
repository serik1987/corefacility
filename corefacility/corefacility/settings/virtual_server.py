from .base import CorefacilityConfiguration


class VirtualServerConfiguration(CorefacilityConfiguration):
    """
    Provides settings for the 'Virtual Server' configuration profile: the application is deployed on the Linux
    server and is unable to provide its administration
    """

    # The base directory where all project and user files were located
    CORE_PROJECT_BASEDIR = "~/.research"

    # Whether the application can manage UNIX groups
    CORE_MANAGE_UNIX_GROUPS = False

    # Whether the application can manage UNIX users
    CORE_MANAGE_UNIX_USERS = False

    # Whether the application can provide another UNIX administration routines
    CORE_UNIX_ADMINISTRATION = False

    # Whether the application can suggest user to provide a certain administration
    CORE_SUGGEST_ADMINISTRATION = False
