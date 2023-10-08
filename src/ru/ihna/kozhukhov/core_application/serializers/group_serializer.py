from rest_framework import serializers

from ru.ihna.kozhukhov.core_application.entity.user import User
from ru.ihna.kozhukhov.core_application.entity.group import Group
from ..entity.entity_sets.user_set import UserSet
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
    governor_id = serializers.IntegerField(required=False, allow_null=True, min_value=1, write_only=True)
    governor = UserListSerializer(many=False, read_only=True, label="Group governor")

    def create(self, data):
        """
        Creates new entity base on the validated data.
        The entity will be automatically stored to the database.

        This is highly important to attach the 'governor' field during the serialization.

        :param data: The validated data.
        :return: new entity
        """
        if 'governor_id' in data:
            if isinstance(self.context['request'].user, User) and self.context['request'].user.is_superuser:
                data['governor'] = UserSet().get(data['governor_id'])
            del data['governor_id']
        if 'governor' not in data:
            data['governor'] = self.context['request'].user
        return super().create(data)

    def update(self, instance, data):
        if "governor_id" in data:
            del data['governor_id']
        return super().update(instance, data)
