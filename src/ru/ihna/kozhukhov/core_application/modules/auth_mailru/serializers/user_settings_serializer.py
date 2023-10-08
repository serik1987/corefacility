from rest_framework import serializers


class UserSettingsSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Mail.Ru account to be attached to the user")
