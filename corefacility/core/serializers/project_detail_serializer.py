from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.entity.entity_exceptions import EntityNotFoundException, EntityException
from core.entity.group import Group, GroupSet

from .project_list_serializer import ProjectListSerializer
from .user_list_serializer import UserListSerializer


class ProjectDetailSerializer(ProjectListSerializer):
    """
    The class is responsible for serialization of project fields during the project settings view
    and data validation during the project settings adjustment.
    """

    description = serializers.CharField(read_only=False, write_only=False, required=False, allow_null=True,
                                        allow_blank=True, max_length=1024, label="Project name")
    root_group_id = serializers.IntegerField(read_only=False, write_only=True, required=False, allow_null=True,
                                             min_value=1, label="Governing group ID or null if the group shall be "
                                                                "created automatically during the project create")
    root_group_name = serializers.CharField(read_only=False, write_only=True, required=False, allow_null=False,
                                            max_length=64,
                                            label="Governing group name (applicable if 'root_group_id field has been "
                                                  "presented but equal to null)")
    governor = UserListSerializer(read_only=True, many=False,
                                  label="The user that is claimed to be project leader")
    project_dir = serializers.ReadOnlyField(
        label="The project dir is located within the '/home' directory, if applicable")
    unix_group = serializers.ReadOnlyField(label="Login to be used for SSH authentication, if applicable")

    def create(self, data):
        """
        Creates new Project from the serialized project data received from the client

        :param data: the serialized data received from the client
        :return: the project itself
        """
        try:
            root_group_id = data['root_group_id']
        except KeyError:
            raise ValidationError({"root_group_id": "This field is mandatory in POST requests"})
        self.calculate_root_group(data, root_group_id)
        return super().create(data)

    def update(self, project, validated_data):
        """
        Changes the project settings using the serialized data.

        :param project: The project which settings shall be updated
        :param validated_data: The data that will be used to update the project settings. The data itself were implied
            to have been already validated
        :return: the updated project instance
        """
        if "root_group_id" in validated_data:
            self.calculate_root_group(validated_data, validated_data["root_group_id"])
        elif "root_group_name" in validated_data:
            del validated_data["root_group_name"]
        return super().update(project, validated_data)

    def calculate_root_group(self, data, root_group_id):
        """
        This function negotiates the POST, PUT and PATCH request input data and the Project object methods.
        The main problem is the request specification requires 'root_group_id' and 'root_group_name' fields
        to be set in proper manner while the 'root_group' field is ignored. On the other hands, the Project object
        method requires the 'root_group' field to be set to a proper instance of the Group object. This method
        solves such a problem

        :param data: the input data to which the 'root_group' field shall be attached and 'root_group_id' and
            'root_group_name' fields shall be deleted
        :param root_group_id: appropriate root group id.
        :return: nothing
        """
        if root_group_id is None:
            user = self.context['request'].user
            try:
                group_name = data['root_group_name']
            except KeyError:
                raise ValidationError({"root_group_name": "The field is required "
                                                          "when the 'root_group_id value is present and equal to null"})
            try:
                group = Group(name=group_name, governor=user)
                group.create()
            except EntityException as e:
                raise ValidationError({"root_group": str(e)})
        else:
            try:
                group = GroupSet().get(root_group_id)
            except EntityNotFoundException:
                raise ValidationError({"root_group_id": "The value is not an ID of the existent group"})
        data['root_group'] = group
        for old_key in ("root_group_id", "root_group_name"):
            if old_key in data:
                del data[old_key]
