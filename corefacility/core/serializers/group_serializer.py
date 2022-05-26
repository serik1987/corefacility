from rest_framework import serializers

from ..entity.group import Group
from .entity_serializer import EntitySerializer
from .user_list_serializer import UserListSerializer


class GroupSerializer(EntitySerializer):
    """
    The class is used for serialization and deserialization user groups.

    The class is suitable for both user and detail serialization.
    """

    entity_class = Group

    id = serializers.ReadOnlyField(label="Group ID")
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=256,
                                 label="Group login")
    governor = UserListSerializer(many=False, read_only=True, label="Group governor")
