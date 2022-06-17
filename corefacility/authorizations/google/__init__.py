from core.entity.entry_points.authorizations import AuthorizationModule


class App(AuthorizationModule):
    """
    Provides functionality for authorization from Google Accounts
    """

    def get_alias(self):
        """
        The alias is Google

        :return:
        """
        return "google"

    def get_name(self):
        """
        The name is "Authorization through Google"

        :return: the widget name
        """
        return "Authorization through Google"

    def get_html_code(self):
        """
        The icon is <div> with two standard CSS styles
        defined in the 'core' module

        :return: the authorization method icon
        """
        return "<div class='auth google'></div>"

    def is_enabled_by_default(self):
        """
        By default, such method is disabled since it shall be properly adjusted to be enabled

        :return: False
        """
        return False

    def try_ui_authorization(self, request):
        pass

    def try_api_authorization(self, request):
        pass

    def process_auxiliary_request(self, request):
        pass
