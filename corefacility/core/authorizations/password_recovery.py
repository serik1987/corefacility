from core.entity.entry_points.authorizations import AuthorizationModule


class PasswordRecoveryAuthorization(AuthorizationModule):
    """
    The password recovery process implies that the user receives the link with his temporary credentials
    by E-mail and then use these credentials for temporary authorization

    This requires specific authorization method through temporary rather then permanent credentials.
    We called this method as 'password recovery authorization'.

    The credentials are temporal because:
    - they are not valid for more than a week
    - they will be destroyed after the user have been authorized
    """

    @property
    def app_class(self):
        """
        Returns the application class
        """
        return "core.authorizations.PasswordRecoveryAuthorization"

    def get_alias(self):
        """
        Some method alias

        :return: some method alias
        """
        return "password_recovery"

    def get_name(self):
        """
        Some method name

        :return: some method name
        """
        return "Password recovery function"

    def get_html_code(self):
        """
        All HTML code for this method is provided in 'core' module, no other functionality is required

        :return: None
        """
        return None

    def is_enabled_by_default(self):
        """
        By default, this method is disabled because it could be rather dangerous

        :return: False
        """
        return False

    def try_ui_authorization(self, request):
        pass

    def try_api_authorization(self, request):
        pass

    def process_auxiliary_request(self, request):
        pass
