from rest_framework import serializers

from core.entity.project import Project

from .entity_serializer import EntitySerializer
from .group_serializer import GroupSerializer


class ProjectListSerializer(EntitySerializer):
    """
    The class is responsible for project settings serialization during the project list output as
    well as for partial validation of some project settings
    """

    entity_class = Project

    id = serializers.ReadOnlyField(label="Project identification number")
    alias = serializers.SlugField(read_only=False, write_only=False, required=True, allow_null=False, max_length=64,
                                  label="Project alias")
    avatar = serializers.ReadOnlyField(source="avatar.url", label="URL for the project icon static file")
    name = serializers.CharField(read_only=False, write_only=False, required=True, allow_null=False, max_length=64,
                                 label="Project name")
    root_group = GroupSerializer(read_only=True, many=False, label="Governing group")
