from django.utils.translation import gettext as _
from rest_framework import status

from core.api_exceptions import CorefacilityAPIException


class MapUploadFileException(CorefacilityAPIException):
    status_code = status.HTTP_400_BAD_REQUEST


class MapProcessingException(CorefacilityAPIException):
    status_code = status.HTTP_400_BAD_REQUEST


class ProjectDirNotDefinedException(MapUploadFileException):

    def __init__(self):
        super().__init__(code="no_project_dir",
                         detail=_("Project's home directory was not defined for the project. "
                                  "Please, ask system administrator to cope with troubles"))


class DataNumberException(MapUploadFileException):

    def __init__(self):
        super().__init__(code="npz_file_data_incorrect", detail=_("Number of variables in the NPZ file is not correct"))


class NotAMapException(MapUploadFileException):

    def __init__(self):
        super().__init__(code="not_a_map", detail=_("The file doesn't contain 2D map consisting from complex numbers"))


class MapNotUploadedException(MapProcessingException):

    def __init__(self):
        super().__init__(code="map_not_uploaded",
                         detail=_("Please, upload the functional map to apply this map processor"))


class UploadFileMissingException(MapProcessingException):

    def __init__(self):
        super().__init__(code="map_missing",
                         detail=_("The functional map has been permanently removed from the server or corrupted. "
                                  "Please, upload it again"))


class TargetMapAliasException(MapProcessingException):

    def __init__(self, target_alias):
        super().__init__(code="map_processing_alias_duplicated",
                         detail=_("Can't process this map because another map with alias '%s' exists") % target_alias)


class TargetMapEmptyException(MapProcessingException):

    def __init__(self):
        super().__init__(code="target_map_empty_exception",
                         detail=_("The target map contains no data"))
