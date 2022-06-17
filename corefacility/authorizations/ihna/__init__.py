from core.entity.entry_points.authorizations import AuthorizationModule


class App(AuthorizationModule):
    """
    Provides an authorization through IHNA RAS website

    Use this module as an example of how to write the authorization module through
    your own institution website
    """

    def get_alias(self):
        """
        The module alias is also 'ihna'

        :return: 'ihna'
        """
        return "ihna"

    def get_name(self):
        """
        The module name

        :return: the module name
        """
        return "Authorization through IHNA website"

    def get_html_code(self):
        """
        The authorization icon is div with standard core module CSS styles

        :return: HTML code for the module icon
        """
        return "<div class='auth ihna'></div>"

    def is_enabled_by_default(self):
        """
        By default, the authorization module is disabled because it doesn't adjusted

        :return: always False
        """
        return False

    def try_ui_authorization(self, request):
        pass

    def try_api_authorization(self, request):
        pass

    def process_auxiliary_request(self, request):
        pass
