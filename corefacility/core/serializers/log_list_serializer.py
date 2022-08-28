from rest_framework import serializers

from .entity_serializer import EntitySerializer
from .user_list_serializer import UserListSerializer


class LogListSerializer(EntitySerializer):
    """
    Serializes the logs when they are downloaded as whole log lists
    """

    id = serializers.ReadOnlyField(help_text="ID")
    request_date = serializers.SerializerMethodField(help_text="Request date and time")
    log_address = serializers.ReadOnlyField(help_text="Full path to the requested resource")
    request_method = serializers.ReadOnlyField(help_text="The method that was used for the request")
    operation_description = serializers.ReadOnlyField(help_text="Human-readable operation description")
    user = UserListSerializer(read_only=True, many=False, help_text="The user that has made the request")
    ip_address = serializers.IPAddressField(protocol="both", read_only=True, help_text="User's IP address")
    geolocation = serializers.ReadOnlyField(help_text="User's geolocation")
    response_status = serializers.ReadOnlyField(help_text="Response status code")

    @staticmethod
    def get_request_date(log):
        """
        Calculates the log's request date
        :param log: the log which request date shall be calculated
        :return: nothing
        """
        return str(log.request_date.get())
