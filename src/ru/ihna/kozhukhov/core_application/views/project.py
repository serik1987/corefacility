from ..generic_views import EntityViewSet, AvatarMixin
from ..entity.project import ProjectSet
from ..serializers import ProjectListSerializer, ProjectDetailSerializer
from ..permissions import ProjectPermission


class ProjectViewSet(AvatarMixin, EntityViewSet):
    """
    Dealing with projects
    """

    entity_set_class = ProjectSet
    list_serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [ProjectPermission]

    list_filters = {
        "name": EntityViewSet.standard_filter_function("q", str)
    }
    """ Filters for the entity list """

    desired_image_width = 300
    """ The image will be cut to this width and next downsampled """

    desired_image_height = 300
    """ The image will be cut to this height and next downsampled """

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
