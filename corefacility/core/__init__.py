from datetime import timedelta

from .entity import CorefacilityModule
from .entity.entity_exceptions import RootModuleDeleteException
from .entity.entry_points import AuthorizationsEntryPoint, SynchronizationsEntryPoint, ProjectsEntryPoint, \
    SettingsEntryPoint


class App(CorefacilityModule):
    """
    The base class for the 'core' application.

    The core application doesn't deal directly with the data but:
    a) manages another application the do deal with the data and simulation
    b) provides base frontend functionality for them
    c) manages projects that are boxes where scientific data and application permissions contain
    d) manages user accounts, do administrative tasks, provides authentication but not authorization
    """

    DEFAULT_MAX_PASSWORD_SYMBOLS = 10
    DEFAULT_AUTH_TOKEN_LIFETIME = timedelta(minutes=30)
    DEFAULT_USER_CAN_CHANGE_HIS_PASSWORD = False

    def get_parent_entry_point(self):
        """
        The 'core' module does not have any entry point

        :return: nothing
        """
        return None

    def get_alias(self):
        """
        The module alias to be used in API

        :return: the module alias
        """
        return "core"
    
    def get_name(self):
        """
        The module name to be display in the settings window

        :return: a string
        """
        return "Core functionality"

    def get_html_code(self):
        """
        Since core functionality doesn't have a parent entry point it doesn't provide any HTML code

        :return: nothing
        """
        return None

    @property
    def is_application(self):
        """
        The core module is not application because it shall be accessible even for unauthorized users
        (otherwise, nobody can authorize)

        :return: False
        """
        return False

    def is_enabled_by_default(self):
        """
        The core module must be always enabled because any module enability can be changed only though core
        module. Once the core module becomes disabled the whole 'corefacility' application will not work
        forever.

        :return: True
        """
        return True

    def get_entry_points(self):
        """
        The 'core' module has four entry points:
        'authorizations' - provides different ways for application authorization
        'synchronizations' - allows to select a specific kind of user account synchronization
        'settings' - allows additional ways to setup the hardware and software installed into your computer
        'projects' - all application dealing with science must be connected here!

        :return: a dictionary containing all four entry points
        """
        return {
            "authorizations": AuthorizationsEntryPoint(),
            "synchronizations": SynchronizationsEntryPoint(),
            "projects": ProjectsEntryPoint(),
            "settings": SettingsEntryPoint(),
        }

    def get_serializer_class(self):
        """
        Defines the serializer class. The serializer class is used to represent module settings in JSON format
        :return: instance of rest_framework.serializers.Serializer class
        """
        from core.serializers.core_settings_serializer import CoreSettingsSerializer
        return CoreSettingsSerializer

    def delete(self):
        """
        Raises an exception because you can't delete the core module.

        Deleting the core module will damage the whole application functionality. Nobody can install or modify
        any module since this is exactly core module that is responsible for this.

        :return: nothing
        """
        raise RootModuleDeleteException()

    def get_max_password_symbols(self):
        """
        Returns the maximum number of symbols in the password

        :return: maximum number of symbols in the password
        """
        return self.user_settings.get("max_password_symbols", self.DEFAULT_MAX_PASSWORD_SYMBOLS)

    def get_auth_token_lifetime(self):
        """
        Returns the authentication token lifetime

        :return: the authentication token lifetime
        """
        return self.user_settings.get("auth_token_lifetime", self.DEFAULT_AUTH_TOKEN_LIFETIME)

    def user_can_change_password(self):
        """
        Returns True if the user can change his password when logged in. False otherwise
        """
        return self.user_settings.get("is_user_can_change_password", self.DEFAULT_USER_CAN_CHANGE_HIS_PASSWORD)
