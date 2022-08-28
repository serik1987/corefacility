from core.generic_views import EntityReadOnlyViewSet
from core.entity.log import LogSet
from core.serializers import LogListSerializer, LogDetailSerializer
from core.permissions import AdminOnlyPermission


class LogViewSet(EntityReadOnlyViewSet):
    """
    Viewing logs
    """

    entity_set_class = LogSet
    list_serializer_class = LogListSerializer
    detail_serializer_class = LogDetailSerializer
    permission_classes = [AdminOnlyPermission]

    list_filters = {
        "request_date_from": EntityReadOnlyViewSet.date_filter_function("from"),
        "request_date_to": EntityReadOnlyViewSet.date_filter_function("to"),
        "ip_address": EntityReadOnlyViewSet.ip_address_function("ip_address"),
        "user": EntityReadOnlyViewSet.user_function("user"),
    }
