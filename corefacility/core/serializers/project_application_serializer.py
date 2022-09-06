from rest_framework import serializers

from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.project_application import ProjectApplication
from core.entity.corefacility_module import CorefacilityModuleSet

from .entity_serializer import EntitySerializer


class ProjectApplicationSerializer(EntitySerializer):
    """
    Provides serialization, deserialization and validation of project-to-application links
    """

    entity_class = ProjectApplication

    uuid = serializers.UUIDField(source="application.uuid", help_text="Application UUID")
    is_enabled = serializers.BooleanField(help_text="is application link enabled?")

    def validate_is_enabled(self, is_enabled):
        """
        Provides additional validation for the project-application link enability
        :param is_enabled: the link enability before the additional validation
        :return: the link enability after the additional validation
        """
        if not is_enabled and not self.context['request'].user.is_superuser:
            raise serializers.ValidationError(
                "Only superusers are allowed to set such value. "
                "To frontend developers: leave this widget only when superuser privileges are granted to the user")
        return is_enabled

    def validate(self, data):
        """
        Provides additional validation of the data
        :param data: data before the additional validation
        :return: data after the additional validation
        """
        module_set = CorefacilityModuleSet()
        module_set.is_application = True
        module_set.is_enabled = True
        try:
            application = module_set.get(data['application']['uuid'])
        except EntityNotFoundException:
            raise serializers.ValidationError("Incorrect module's UUID")
        if application.permissions != "add" and not self.context['request'].user.is_superuser:
            raise serializers.ValidationError("The user has no permissions to add this application. "
                                              "To frontend developers: please, exclude this application from the "
                                              "application list")
        data['application'] = application
        return data

    def create(self, data):
        """
        Creates project application from the validated data
        :param data: the validated data
        :return: the project application that has already been created
        """
        data['project'] = self.context['request'].project
        return super().create(data)
