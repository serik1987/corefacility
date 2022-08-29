from rest_framework.exceptions import NotFound

from core.generic_views.viewsets import EntityReadOnlyViewSet
from core.entity.log import LogSet
from core.entity.log_record import LogRecordSet
from core.entity.entity_exceptions import EntityNotFoundException
from core.serializers import LogRecordSerializer
from core.permissions import AdminOnlyPermission


class LogRecordViewSet(EntityReadOnlyViewSet):
    """
    Reading records for a given log
    """

    entity_set_class = LogRecordSet
    list_serializer_class = LogRecordSerializer
    detail_serializer_class = LogRecordSerializer
    permission_classes = [AdminOnlyPermission]

    def filter_queryset(self, queryset):
        """
        Provides additional queryset filtering
        :param queryset: the queryset before adjusting all filters
        :return: queryset after adjusting all filters
        """
        queryset = super().filter_queryset(queryset)
        try:
            log_id = int(self.kwargs['log_id'])
            queryset.log = LogSet().get(log_id)
        except (EntityNotFoundException, ValueError):
            raise NotFound()
        return queryset
