from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSettingsSerializer(serializers.Serializer):
    """
    Provides de-serialization and validation for the user settings
    """

    GMAIL_SUFFIX = "@gmail.com"

    email = serializers.EmailField(help_text="Google account name (an E-mail")

    def validate_email(self, email):
        """
        Provides additional check for the E-mail
        :param email: the e-mail before check
        :return: the e-mail after check
        """
        if not email.endswith(self.GMAIL_SUFFIX):
            raise ValidationError(_("The e-mail must be ended to @gmail.com"))
        return email
