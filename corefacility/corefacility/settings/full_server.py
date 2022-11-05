from configurations import values
from .base import CorefacilityConfiguration


class FullServerConfiguration(CorefacilityConfiguration):
    """
    Defines settings for the 'Full Server' configuration profile: the application is deployed on the Linux
    server and can be used for its administration
    """

    admin_allowed = True

    # E-mail support
    EMAIL_SUPPORT = False

    # The list of allowed IPs. The application will perform operating system administrator routines only for
    # remote clients which IP addresses are from the list
    ALLOWED_IPS = values.ListValue([])

    # The base directory where all project and user files were located
    CORE_PROJECT_BASEDIR = "/home"

    # Whether the application can manage UNIX groups
    CORE_MANAGE_UNIX_GROUPS = True

    # Whether the application can manage UNIX users
    CORE_MANAGE_UNIX_USERS = True

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
