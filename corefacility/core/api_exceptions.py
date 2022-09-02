from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as base_handler

from core.entity.entity_exceptions import EntityException


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


class EntityProcessingException(CorefacilityAPIException):
    """
    Raises during any error at the entity layer.
    """
    status_code = status.HTTP_400_BAD_REQUEST


class OperatingSystemException(EntityProcessingException):
    """
    Raises at any operating system exceptions
    """
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, os_error):
        """
        Initializes the exception
        :param os_error: another_exception
        """
        super().__init__(code="os_error", detail=str(os_error))


class FileFormatException(CorefacilityAPIException):
    """
    Raises when bad file format has been uploaded
    """

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        super().__init__(code="file_upload_error", detail=_("This file type is not uploadable"))


class AvatarResolutionTooSmallException(CorefacilityAPIException):
    """
    Raises when the user tries to upload too small avatar
    """

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        super().__init__(code="file_upload_error", detail=_("The image resolution is too small"))


def exception_handler(exc, context):
    """
    Defines standard exception handler for all corefacility project.

    :param exc: exception to handle
    :param context: some useless parameter
    :return: REST framework response containing handled exception
    """
    if isinstance(exc, EntityException):
        exc = EntityProcessingException(code=exc.__class__.__name__, detail=str(exc))
    response = base_handler(exc, context)
    if hasattr(exc, "detail") and hasattr(exc.detail, "code") and exc.detail.code:
        response.data["code"] = str(exc.detail.code)
    return response
