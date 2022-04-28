from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .user_list_serializer import UserListSerializer


class UserDetailSerializer(UserListSerializer):
    """
    Serializer for the user detail view
    """
    is_password_set = serializers.SerializerMethodField(method_name="get_password_set", label="Password")
    email = serializers.EmailField(required=False, allow_blank=True, max_length=254, label="E-mail")
    phone = serializers.RegexField("^\\+?[\\d\\(\\)\\s\\-]+$",
                                   required=False, allow_blank=True, max_length=20, label="Phone number",
                                   error_messages={
                                       "invalid": _("Enter a valid phone number.")
                                   })
    is_locked = serializers.BooleanField(required=False, label="Is locked")
    is_superuser = serializers.BooleanField(required=False, label="Is superuser")
    is_support = serializers.ReadOnlyField(label="Is support")
    unix_group = serializers.ReadOnlyField(label="Unix group")
    home_dir = serializers.ReadOnlyField(label="Home directory")

    def get_password_set(self, user):
        """
        Checks whether the user has set its password

        :param user: the user which password shall be checked
        :return: True if the user has set its password, False otherwise
        """
        return len(repr(user.password_hash)) > 0
