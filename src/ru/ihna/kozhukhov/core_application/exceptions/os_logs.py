from django.utils.translation import gettext as _
from rest_framework import status

from ru.ihna.kozhukhov.core_application.exceptions.api_exceptions import CorefacilityAPIException


class OsLogException(CorefacilityAPIException):
    """
    This is the base exception for all errors specific to the /api/v1/os-logs/ request
    """
    status_code = status.HTTP_400_BAD_REQUEST


class NoLogDirectoryException(OsLogException):
    """
    Thrown when no /var/log/corefacility directory exists.
    """

    def __init__(self):
        super().__init__(
            code="no_log_directory_exception",
            detail=_("The directory /var/log/corefacility doesn't exists. Please, complete the corefacility "
                     "installation by adjustment of rsyslog daemon in such a way as it writes logs directly to "
                     "/var/log/corefacility/syslog and /var/log/corefacility/auth.log files")
        )