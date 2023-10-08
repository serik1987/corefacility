from rest_framework.permissions import IsAuthenticated

from ..generic_views import EntityListView
from ..entity.access_level import AccessLevelSet
from ..serializers import AccessLevelSerializer


class AccessLevelView(EntityListView):
    """
    Shows the access level list
    """

    entity_set_class = AccessLevelSet
    list_serializer_class = AccessLevelSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    list_filters = {

    }
