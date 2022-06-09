from core.generic_views import EntityViewSet
from core.entity.project import ProjectSet
from core.serializers import ProjectListSerializer, ProjectDetailSerializer


class ProjectViewSet(EntityViewSet):
    """
    Dealing with projects
    """

    entity_set_class = ProjectSet
    list_serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    list_filters = {
        "name": EntityViewSet.standard_filter_function("q", str)
    }
    """ Filters for the entity list """

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        entity_set = super().filter_queryset(queryset)
        if not self.request.user.is_superuser:
            entity_set.user = self.request.user
        return entity_set
