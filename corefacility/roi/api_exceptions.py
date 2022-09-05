from django.utils.translation import gettext as _

from imaging.api_exceptions import MapProcessingException


class BadDimensionsException(MapProcessingException):

    def __init__(self):
        super().__init__(code="bad_dimensions",
                         detail=_("To process the map please, give map dimensions in um"))


class NoPinwheelException(MapProcessingException):

    def __init__(self):
        super().__init__(code="no_pinwheels",
                         detail=_("To process the map please, mark at least one pinwheel center"))
