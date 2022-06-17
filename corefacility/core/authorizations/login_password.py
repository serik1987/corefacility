from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.user import User
from core.serializers import LoginPasswordSerializer


class LoginPasswordAuthorization(AuthorizationModule):
    """
    This is the base class for all authorization methods that requires login and password only.
    """

    def try_api_authorization(self, request):
        """
        Performs the API authorization.
        The API authorization will be performed manually when the client send '/api/login/' request to the server.
        This function shall process the request and find an appropriate user. There is not neccessity to generate
        authentication token for this particular user.

        :param request: REST framework request
        :return: an authorized user in case of successful authorization. None if authorization fails. The function
        shall not generate authorization token, just return the user. The user if core.entity.user.User instance.
        """
        credentials = self.get_credentials(request)
        if isinstance(credentials, LoginPasswordSerializer):
            user = self.authorize(credentials.validated_data['login'], credentials.validated_data['password'])
            if user is not None:
                request.corefacility_log.request_body = "***"
            return user

    def try_ui_authorization(self, request):
        """
        Performs the UI authorization.
        Please, note that UI authorization is not available for all methods that require login and password

        :param request: REST framework request
        :return: always None
        """
        return None

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

    def get_credentials(self, request):
        """
        Returns the credentials containing in the request body

        :param request: the request received from the client
        :return: nothing
        """
        if not hasattr(request, "corefacility_credentials"):
            credentials = LoginPasswordSerializer(data=request.data)
            if credentials.is_valid():
                request.corefacility_credentials = credentials
            else:
                return None
        return request.corefacility_credentials

    def authorize(self, login: str, password: str) -> User:
        """
        Performs an immediate user's authorization

        :param login: user's login
        :param password: user's password
        :return: the user authorized
        """
        raise NotImplementedError("LoginPasswordAuthorization.authorize")
