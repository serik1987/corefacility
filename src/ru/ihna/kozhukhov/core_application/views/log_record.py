from rest_framework.exceptions import NotFound

from ..generic_views.viewsets import EntityReadOnlyViewSet
from ..entity.log import LogSet
from ..entity.log_record import LogRecordSet
from ..exceptions.entity_exceptions import EntityNotFoundException
from ..serializers import LogRecordSerializer
from ..permissions import AdminOnlyPermission


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
