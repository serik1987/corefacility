from core.entity.entry_points.authorizations import AuthorizationModule


class App(AuthorizationModule):
    """
    Provides the authorization through the MAIL.RU system
    """

    def get_alias(self):
        """
        Returns the authorization method alias

        :return: always 'mailru'
        """
        return "mailru"

    def get_name(self):
        """
        Returns the authorization method name.
        The method name will always be displayed in the settings window and as
        tooltip for the login window

        :return: the authorization method name.
        """
        return "Authorization through Mail.ru"

    def get_html_code(self):
        """
        The icon related to this authorization method is always a <div>
        with two standard CSS classes defined in the 'core' module

        :return: the method HTML code
        """
        return "<div class='auth mailru'></div>"

    def is_enabled_by_default(self):
        """
        By default this method is disabled because one requires it to be properly configured

        :return: always False
        """
        return False

    def try_ui_authorization(self, request):
        pass

    def try_api_authorization(self, request):
        pass

    def process_auxiliary_request(self, request):
        pass
