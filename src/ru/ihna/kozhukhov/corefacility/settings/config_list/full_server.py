from configurations import values
from ru.ihna.kozhukhov.corefacility.settings.config_list.base import CorefacilityConfiguration


class FullServerConfiguration(CorefacilityConfiguration):
    """
    Defines settings for the 'Full Server' configuration profile: the application is deployed on the Linux
    server and can be used for its administration
    """

    admin_allowed = True

    # E-mail support
    EMAIL_SUPPORT = True

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

    # Root only is allowed to run CLI (this is protection against HTTP + SSH hacking => when the hacker registers
    # as simple user, gain the SSH access and next use CLI in order to avoid the model layer).
    CORE_ROOT_ONLY = True

    # Owner of the corefacility process that is responsible for processing HTTP requests.
    CORE_WORKER_PROCESS_USER = values.Value('www-data')

    @classmethod
    def check_config_possibility(cls):
        """
        Checks whether the configuration profile is applicable. If not throws MalformedConfiguration

        :return: Nothing.
        """
        cls.check_posix()
