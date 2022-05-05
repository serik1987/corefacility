from rest_framework import serializers

from .user_detail_serializer import UserDetailSerializer


class ProfileSerializer(UserDetailSerializer):
    """
    Adjusts the profile serialization and deserialization
    """

    login = serializers.ReadOnlyField(label="Username (login)")
    is_password_set = None
    is_locked = None
    is_superuser = None
    is_support = None
