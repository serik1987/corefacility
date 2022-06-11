from rest_framework import serializers

from .entity_serializer import EntitySerializer


class AccessLevelSerializer(EntitySerializer):
    """
    Converts user access levels from AccessLevel type to Python primitives
    """

    id = serializers.ReadOnlyField(label="Access level ID (to be used for permission set)")
    type = serializers.ReadOnlyField(label="Project or application access level?")
    alias = serializers.ReadOnlyField(label="Access level alias (to be used in permission's Python code)")
    name = serializers.ReadOnlyField(label="Human-Readable permission name")
