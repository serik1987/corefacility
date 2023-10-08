from rest_framework import serializers


class LoginPasswordSerializer(serializers.Serializer):
    """
    De-serializes user's login and password
    """

    login = serializers.CharField(write_only=True, label="Authorization login")
    password = serializers.CharField(write_only=True, label="User's password")
