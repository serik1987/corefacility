from rest_framework import serializers


class PermissionOutputSerializer(serializers.Serializer):
    """
    Serializers a particular project or application permission
    """

    group_id = serializers.ReadOnlyField(source="group.id", label="group ID")
    group_name = serializers.ReadOnlyField(source="group.name", label="Human-readable group name")
    access_level_id = serializers.ReadOnlyField(source="access_level.id",
                                                label="Access level ID (to be used in the permission set/modify)")
    access_level_alias = serializers.ReadOnlyField(source="access_level.alias",
                                                   label="Access level alias (to be used in the Python code)")
    access_level_name = serializers.ReadOnlyField(source="access_level.name",
                                                  label="Human-readable name of the access level")

    def update(self, instance, validated_data):
        raise NotImplemented("This is read-only serializer")

    def create(self, validated_data):
        raise NotImplemented("This is read-only serializer")
