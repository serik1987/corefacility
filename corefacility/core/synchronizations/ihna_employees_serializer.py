from rest_framework import serializers

from core.serializers import ModuleSettingsSerializer


class IhnaEmployeesSerializer(ModuleSettingsSerializer):
    """
    Provides serialization of settings of IhnaSynchronization module
    """

    auto_add = serializers.BooleanField(source="user_settings.auto_add", default=True,
                                        help_text="Add new users")
    auto_update = serializers.BooleanField(source="user_settings.auto_update", default=True,
                                           help_text="Update users")
    auto_remove = serializers.BooleanField(source="user_settings.auto_remove", default=True,
                                           help_text="Remove users")

    ihna_website = serializers.URLField(source="user_settings.ihna_website", default="https://www.ihna.ru",
                                        help_text="Ihna website URL")
    language = serializers.ChoiceField(source="user_settings.language", default="ru",
                                       choices=[
                                           ("ru", "Russian"),
                                           ("en", "English"),
                                       ],
                                       help_text="The Website language")
    page_length = serializers.IntegerField(source="user_settings.page_length", default=20,
                                           min_value=6, help_text="The page length")
