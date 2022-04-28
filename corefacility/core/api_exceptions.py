from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class CorefacilityAPIException(APIException):
    """
    This is the base class for all API exceptions
    """
    pass

