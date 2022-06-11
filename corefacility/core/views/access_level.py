from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from core.generic_views import EntityListView
from core.models.enums import LevelType
from core.entity.access_level import AccessLevelSet
from core.serializers import AccessLevelSerializer


def access_level_filter(query_params):
    """
    Provides the access level type filter

    :param query_params: params in the query
    :return: nothing
    """
    try:
        level_type = query_params["type"]
    except KeyError:
        return None
    try:
        type_object = LevelType(level_type)
    except ValueError:
        raise ValidationError({"detail": "The access level type is incorrect or unknown", "code": "ValueError"})
    return type_object


class AccessLevelView(EntityListView):
    """
    Shows the access level list
    """

    entity_set_class = AccessLevelSet
    list_serializer_class = AccessLevelSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    list_filters = {
        "type": access_level_filter
    }
