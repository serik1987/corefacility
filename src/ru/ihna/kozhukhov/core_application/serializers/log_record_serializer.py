from rest_framework import serializers

from .entity_serializer import EntitySerializer


class LogRecordSerializer(EntitySerializer):
    """
    Converts the LogRecord entity to the representation suitable for conversion to JSON format
    """

    id = serializers.ReadOnlyField(help_text="Log record ID")
    record_time = serializers.SerializerMethodField(help_text="Date and time for log record production")
    level = serializers.SerializerMethodField(help_text="Level of the record message")
    message = serializers.ReadOnlyField(help_text="Log record message")

    @staticmethod
    def get_record_time(log_record):
        """
        Finds date and time, where log record has been made
        :param log_record: the log record
        :return: a string containing date and time
        """
        return str(log_record.record_time.get())

    @staticmethod
    def get_level(log_record):
        """
        Returns a CSS style corresponding to the log record level
        :param log_record: the log record
        :return: proper CSS style
        """
        return str(log_record.level).lower()
