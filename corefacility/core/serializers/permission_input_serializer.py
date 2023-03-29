from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.entity.group import GroupSet
from core.entity.access_level import AccessLevelSet
from core.entity.permission import Permission
from core.entity.entity_exceptions import EntityNotFoundException


class PermissionInputSerializer(serializers.Serializer):
    """
    Provides short serialization of the Access Control Item (just returns group_id and access_level_id)
    and deserialization
    """

    group_id = serializers.IntegerField(min_value=1, label="ID for the user's group put into the ACL")
    access_level_id = serializers.IntegerField(min_value=1,
                                               label="ID for a given access level",
                                               help_text="Use proper GET requests to inquiry about access level IDs")

    def update(self, instance, validated_data):
        raise NotImplemented("The serializer can't work in the update mode")

    def create(self, validated_data):
        """
        Transforms the validated data to Permission instance

        :param validated_data: the validated data
        :return: Permission instance
        """
        try:
            group = GroupSet().get(validated_data["group_id"])
            access_level = AccessLevelSet().get(validated_data["access_level_id"])
        except EntityNotFoundException:
            raise ValidationError({
                "detail": "the group_id and/or access_level_id fields doesn't refer to valid argument"
            })
        permission = Permission(group=group, access_level=access_level)
        return permission
