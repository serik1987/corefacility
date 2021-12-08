from core.entity.entry_points.authorizations import AuthorizationModule


class AutomaticAuthorization(AuthorizationModule):
    """
    The module requires no information from the user and no cookie from the Web browser and do the
    following (of course, if and only if this method is enabled):
    - if 'support' user account is locked authorization fails;
    - if at least one other authorization method is enabled authorization fails;
    - in any other case the authorization is success

    This method is suitable for 'simple desktop' and 'extended desktop' configuration profile
    when one person only uses the application and hence there is no necessity to provide credentials.
    """

    def get_alias(self):
        """
        The method alias

        :return: the method alias
        """
        return "auto"

    def get_name(self):
        """
        The method name

        :return: the method name
        """
        return "Automatic authorization"

    def get_html_code(self):
        """
        If this method is enabled and the user passes the authorization a main window will be given,
        the login form will not be presented. Hence, no additional HTML code is required for this
        authorization method

        :return: None
        """
        return None

    def is_enabled_by_default(self):
        """
        The method is enabled immediately after installation because nobody can login in any other way.
        When the superuser is logged in using this method he must create his own account, turn on
        the standard authorization method, turn off this authorization method, lock the 'support' account
        and reload the browser window

        :return: True
        """
        return True
