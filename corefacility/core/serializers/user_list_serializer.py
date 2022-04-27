from rest_framework import serializers

from . import EntitySerializer
from ..entity.user import User


class UserListSerializer(EntitySerializer):
    """
    Serializes the whole user list
    """

    entity_class = User

    id = serializers.IntegerField(read_only=True)
    login = serializers.CharField(required=True, allow_blank=False, max_length=100)
    name = serializers.CharField(required=False, allow_blank=True, max_length=100)
