from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    """
    Serializers a particular project or application permission
    """

    group_id = serializers.ReadOnlyField(source="group.id", label="group ID")
    group_name = serializers.ReadOnlyField(source="group.name", label="Human-readable group name")
    access_level_id = serializers.IntegerField(min_value=1, required=True,
                                               label="Access level ID (to be used in the permission set/modify)")
    access_level_alias = serializers.ReadOnlyField(label="Access level alias (to be used in the Python code)")
    access_level_name = serializers.ReadOnlyField(label="Human-readable name of the access level")
