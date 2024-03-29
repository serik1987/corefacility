from rest_framework import serializers

from .log_list_serializer import LogListSerializer
from .log_record_serializer import LogRecordSerializer


class LogDetailSerializer(LogListSerializer):
    """
    Serializes logs to deliver them to the client application in stand-alone mode (i.e., without any lists)
    """

    request_body = serializers.ReadOnlyField(help_text="Raw body request")
    input_data = serializers.ReadOnlyField(help_text="Human-readable description of the input data")
    response_body = serializers.ReadOnlyField(help_text="Raw response body")
    output_data = serializers.ReadOnlyField(help_text="Human-readable description of the output data")
    records = LogRecordSerializer(many=True, read_only=True, help_text="List of all records related to the log")
