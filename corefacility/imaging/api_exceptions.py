from django.utils.translation import gettext as _
from rest_framework import status

from core.api_exceptions import CorefacilityAPIException


class MapUploadFileException(CorefacilityAPIException):
    status = status.HTTP_400_BAD_REQUEST


class DataNumberException(MapUploadFileException):

    def __init__(self):
        super().__init__(code="npz_file_data_incorrect", detail=_("Number of variables in the NPZ file is not correct"))


class NotAMapException(MapUploadFileException):

    def __init__(self):
        super().__init__(code="not_a_map", detail=_("The file doesn't contain 2D map consisting from complex numbers"))
