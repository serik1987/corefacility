from ..generic_views import EntityViewSet
from ..entity.group import GroupSet
from ..serializers import GroupSerializer
from ..permissions import GroupPermission


class GroupViewSet(EntityViewSet):
    """
    Deals with list of groups.
    """

    list_filters = {
        "name": EntityViewSet.standard_filter_function("q", str),
    }

    entity_set_class = GroupSet
    list_serializer_class = GroupSerializer
    detail_serializer_class = GroupSerializer
    permission_classes = [GroupPermission]

    def filter_queryset(self, queryset):
        """
        Provides additional queryset filtration according to security considerations.

        :param queryset: the initial queryset
        :return: the filtered queryset
        """
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if not user.is_superuser:
            queryset.user = user
        return queryset
