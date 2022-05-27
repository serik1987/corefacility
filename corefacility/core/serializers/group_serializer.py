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

    def create(self, data):
        """
        Creates new entity base on the validated data.
        The entity will be automatically stored to the database.

        This is highly important to attach the 'governor' field during the serialization.

        :param data: The validated data.
        :return: new entity
        """
        data['governor'] = self.context['request'].user
        return super().create(data)
