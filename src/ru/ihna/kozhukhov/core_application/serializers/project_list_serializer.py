from rest_framework import serializers

from ..entity.project import Project

from .entity_serializer import EntitySerializer
from .group_serializer import GroupSerializer
from .user_list_serializer import UserListSerializer


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
    governor = UserListSerializer(read_only=True, many=False,
                                  label="The user that is claimed to be project leader")

    def to_representation(self, project):
        """
        Converts the core.entity.project.Project instance to its serialized representation

        :param project: the entity itself
        :return: its serialized representation
        """
        representation = super().to_representation(project)
        if self.context['request'].user.is_superuser:
            representation["user_access_level"] = "full"
            representation["is_user_governor"] = True
        else:
            representation["user_access_level"] = project.get_proper_access_level(project.user_access_level)
            representation["is_user_governor"] = project.is_user_governor
        return representation
