from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class SynchronizationError(APIException):
    """
    This is the base class for all synchronization routines
    """
    pass


class TeapotError(SynchronizationError):
    """
    Trying to synchronize responses when all synchronizers are switched off
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    def __init__(self):
        super().__init__(_("Unable to perform synchronization because all synchronizers were switched off"))


class RemoteServerError(SynchronizationError):
    """
    Trying to synchronize responses when the remote server can't return the successful response
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    def __init__(self):
        super().__init__(_("Unable to perform synchronization due to the temporary problems on remote server"))


class UserRemoveConsistencyError(SynchronizationError):
    """
    Trying to remove a user that has been currently logged in
    """

    def __init__(self):
        super().__init__(_("Failed to remove a user: the user has been currently logged in"))
