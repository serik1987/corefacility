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

    status_code = status.HTTP_418_IM_A_TEAPOT

    def __init__(self):
        super().__init__(_("Unable to perform synchronization because all synchronizers were switched off"))
