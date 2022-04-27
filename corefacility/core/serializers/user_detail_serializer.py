from rest_framework import serializers
from .user_list_serializer import UserListSerializer


class UserDetailSerializer(UserListSerializer):
    """
    Serializer for the user detail view
    """
    email = serializers.CharField(required=False, allow_blank=True, max_length=254)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
