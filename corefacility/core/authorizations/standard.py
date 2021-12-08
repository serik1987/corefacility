from core.entity.entry_points.authorizations import AuthorizationModule


class StandardAuthorization(AuthorizationModule):
    """
    This is a pseudo-module responsible for the standard authorization process

    This is a pseudo-module because it doesn't contain its own database information and API
    but can be configured using the control panel and behaves like any other core authorization
    module
    """

    def get_alias(self):
        """
        The authorization method alias is 'standard'

        :return: 'standard'
        """
        return "standard"

    def get_name(self):
        """
        The authorization method name is always 'Standard authorization'

        :return: always 'Standard authorization'
        """
        return "Standard authorization"

    def get_html_code(self):
        """
        The authorization icons allows the user to select alternative authorization
        methods, so the standard authorization method doesn't require any icons

        :return:
        """
        return None

    def is_enabled_by_default(self):
        """
        By default, the user can enter to the application without any required authorization.
        This allows the system administrator to automatically login as 'support' and then
        adjust the authorization process

        :return: always False
        """
        return False
