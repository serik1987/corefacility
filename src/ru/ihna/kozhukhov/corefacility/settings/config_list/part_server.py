from ru.ihna.kozhukhov.corefacility.settings.config_list.base import CorefacilityConfiguration


class PartServerConfiguration(CorefacilityConfiguration):
    """
    Defines settings for the 'Part Server' configuration profile: the application is deployed on the Linux
    server and can suggest some ways for its administration
    """

    admin_allowed = True

    # The base directory where all project and user files were located
    CORE_PROJECT_BASEDIR = "/home"

    # E-mail support
    EMAIL_SUPPORT = True

    # Whether the application can manage UNIX groups
    CORE_MANAGE_UNIX_GROUPS = True

    # Whether the application can manage UNIX users
    CORE_MANAGE_UNIX_USERS = True

    # Whether the application can provide another UNIX administration routines
    CORE_UNIX_ADMINISTRATION = False

    # Whether the application can suggest user to provide a certain administration
    CORE_SUGGEST_ADMINISTRATION = True

    # Root only is allowed to run CLI (this is protection against HTTP + SSH hacking => when the hacker registers
    # as simple user, gain the SSH access and next use CLI in order to avoid the model layer).
    CORE_ROOT_ONLY = True

    @classmethod
    def check_config_possibility(cls):
        """
        Checks whether the configuration profile is applicable. If not throws MalformedConfiguration

        :return: Nothing.
        """
        cls.check_posix()
