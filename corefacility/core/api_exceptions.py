from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class CorefacilityAPIException(APIException):
    """
    This is the base class for all API exceptions
    """
    pass


class BadOutputProfileException(CorefacilityAPIException):
    """
    Raises when request output profile is not allowed or supported.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "output_profile_error"
    default_detail = "The output profile is invalid."
