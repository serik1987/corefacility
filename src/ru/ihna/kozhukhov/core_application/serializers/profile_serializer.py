from rest_framework import serializers

from .user_detail_serializer import UserDetailSerializer


class ProfileSerializer(UserDetailSerializer):
    """
    Adjusts the profile serialization and deserialization
    """

    login = serializers.ReadOnlyField(label="Username (login)")
    is_password_set = None
    is_locked = serializers.ReadOnlyField(label="Is locked (is_locked)")
    is_superuser = serializers.ReadOnlyField(label="Is superuser (is_superuser")
    is_support = serializers.ReadOnlyField(label="Is support (is_support)")
