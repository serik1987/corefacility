from rest_framework import serializers
from core.serializers import ModuleSettingsSerializer
from .password_recovery import PasswordRecoveryAuthorization


class PasswordRecoverySerializer(ModuleSettingsSerializer):
	"""
	Provides serialization, deserialization and validation of the password recovery
	module settings
	"""
	password_recovery_lifetime = serializers.DurationField(
		source='user_settings.password_recovery_lifetime',
		default=PasswordRecoveryAuthorization.DEFAULT_PASSWORD_RECOVERY_LIFETIME,
		help_text='After given amount of time the activation link will be invalid'
	)
