from rest_framework import serializers
from ...serializers import ModuleSettingsSerializer
from ru.ihna.kozhukhov.core_application.modules.auth_password_recovery.__init__ import PasswordRecoveryAuthorization


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
