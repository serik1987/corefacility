from core.entity.entry_points.authorizations import AuthorizationModule


class UnixAuthorization(AuthorizationModule):
    """
    Provides an authorization using credentials saved in the
    /etc/passwd and /etc/shadow files. Is you turned this
    method ON your accounts will be actually synchronized with
    the operating system accounts

    The authorization method doesn't work in non-UNIX operating
    systems (you can't simply enable this)

    This is a pseudo-module since it doesn't have its own database
    information and API
    """

    @property
    def app_class(self):
        """
        Returns the application class
        """
        return "core.authorizations.UnixAuthorization"

    def get_alias(self):
        """
        Always 'unix'

        :return: 'unix'
        """
        return 'unix'

    def get_name(self):
        """
        Returns the authorization method name

        :return: the authorization method name
        """
        return "Authorization through UNIX account"

    def get_html_code(self):
        """
        Returns None since the method will be applied automatically and doesn't require any user interaction

        :return: None
        """
        return None

    def is_enabled_by_default(self):
        """
        By default this method is disabled and nobody can enable it in non-UNIX operating system

        :return: always False
        """
        return False

    def try_ui_authorization(self, request):
        pass

    def try_api_authorization(self, request):
        pass

    def process_auxiliary_request(self, request):
        pass
