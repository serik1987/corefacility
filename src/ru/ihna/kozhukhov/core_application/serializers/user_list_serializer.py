from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from . import EntitySerializer
from ru.ihna.kozhukhov.core_application.entity.user import User


class UserListSerializer(EntitySerializer):
    """
    Serializes the whole user list
    """

    entity_class = User

    id = serializers.ReadOnlyField(label="Identification number")
    login = serializers.SlugField(required=True, allow_blank=False, max_length=100,
                                  label="Username (login)",
                                  error_messages={
                                      "invalid":
                                          _('Enter a valid login consisting of letters, numbers, '
                                            'underscores or hyphens.')
                                  })
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100,
                                 label="First name")
    surname = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100,
                                    label="Last name")
    avatar = serializers.ReadOnlyField(source="avatar.url", label="Avatar URL")
