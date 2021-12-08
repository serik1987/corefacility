from core.entity.entry_points.authorizations import AuthorizationModule


class App(AuthorizationModule):
    """
    Provides an authorization through the web browser cookie which means the following:

    1) During the first call this method skips the authorization. However, after successful
    authorization it sends Cookie to the user with a special authorization token

    2) Next, if the user sends cookie with this token, it will be authorized automatically
    """

    def get_alias(self):
        """
        The authorization method alias

        :return: 'cookie'
        """
        return "cookie"

    def get_name(self):
        """
        The authorization method name

        :return: the method name
        """
        return "Authorization through Cookie"

    def get_html_code(self):
        """
        The method doesn't have HTML code because it doesn't require
        additional actions from the user to authorize it

        :return: None, of course
        """
        return None

    def is_enabled_by_default(self):
        """
        False because authorization through Cookie may not be safe

        :return: always False
        """
        return False
