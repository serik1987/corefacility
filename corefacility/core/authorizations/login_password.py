from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from rest_framework.exceptions import Throttled

from core.utils import get_ip
from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.user import User
from core.entity.failed_authorization import FailedAuthorization, FailedAuthorizationSet
from core.serializers import LoginPasswordSerializer


class LoginPasswordAuthorization(AuthorizationModule):
    """
    This is the base class for all authorization methods that requires login and password only.
    """

    DEFAULT_MAX_FAILED_AUTHORIZATION_NUMBER = 50
    DEFAULT_MIN_WAIT = 1
    DEFAULT_MAX_WAIT = 10
    THROTTLE_LIFETIME = timedelta(minutes=15)

    _request = None

    def try_api_authorization(self, request):
        """
        Performs the API authorization.
        The API authorization will be performed manually when the client send '/api/login/' request to the server.
        This function shall process the request and find an appropriate user. There is not a necessity to generate
        authentication token for this particular user.

        :param request: REST framework request
        :return: an authorized user in case of successful authorization. None if authorization fails. The function
        shall not generate authorization token, just return the user. The user is core.entity.user.User instance.
        """
        self._request = request
        request.corefacility_log.request_body = "***"
        credentials = self.get_credentials(request)
        if isinstance(credentials, LoginPasswordSerializer):
            user = self.authorize(credentials.validated_data['login'], credentials.validated_data['password'])
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
        Performs an immediate user's authorization.
        The method should contain call of _notify_failed_authorization and _throttle_authorization methods in order
        to protect corefacility from the brute force attack

        :param login: user's login
        :param password: user's password
        :return: the user authorized
        """
        raise NotImplementedError("LoginPasswordAuthorization.authorize")

    def get_max_failed_authorization_number(self):
        """
        Returns maximum number of failed authorizations after which throttling will be applied
        """
        return self.user_settings.get("max_failed_authorization_number", self.DEFAULT_MAX_FAILED_AUTHORIZATION_NUMBER)

    def get_max_wait(self):
        """
        Returns the max wait time
        """
        return self.DEFAULT_MAX_WAIT

    def _notify_failed_authorization(self, user: User):
        """
        Adds +1 failed authorization to the database in order to throttle it in the future
        :param user: user that was recovered using the login
        :return: nothing
        """
        if self._request is not None:
            FailedAuthorization.add(get_ip(self._request), user)

    def _throttle_authorization(self, user: User):
        """
        Throttles an authorization if there are too many attempts to guess user login and password
        :param user: user which password is guessed
        :return: nothing
        """
        max_fail_number = self.get_max_failed_authorization_number()
        min_wait = self.DEFAULT_MIN_WAIT
        max_wait = self.get_max_wait()
        ip = get_ip(self._request)
        actual_fail_number = FailedAuthorization.get_failed_authorizations_number(ip, user, self.THROTTLE_LIFETIME)
        if actual_fail_number > max_fail_number:
            failed_authorization_set = FailedAuthorizationSet()
            failed_authorization_set.ip = ip
            failed_authorization_set.user = user
            failed_authorization = failed_authorization_set[0]
            failed_authorization_time = failed_authorization.auth_time.get()
            current_time = make_aware(datetime.now())
            actual_wait_time = (current_time - failed_authorization_time).seconds
            expected_wait_time = (actual_fail_number - max_fail_number) * min_wait
            if expected_wait_time < 0:
                expected_wait_time = 0
            if expected_wait_time > max_wait:
                expected_wait_time = max_wait
            if actual_wait_time < expected_wait_time:
                raise Throttled(expected_wait_time)
