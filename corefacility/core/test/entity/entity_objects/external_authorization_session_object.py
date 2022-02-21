from datetime import timedelta

from core.entity.external_authorization_session import ExternalAuthorizationSession
from core.entity.entity_fields.field_managers.entity_password_manager import EntityPasswordManager

from authorizations.google import App as GoogleApp
from authorizations.ihna import App as IhnaApp

from .entity_object import EntityObject


class ExternalAuthorizationSessionObject(EntityObject):

    _entity_class = ExternalAuthorizationSession

    _default_create_kwargs = {
        "authorization_module": GoogleApp()
    }

    _default_change_kwargs = {
        "authorization_module": IhnaApp()
    }

    _last_password = None

    def __init__(self, use_defaults=True, **kwargs):
        """
        Creates the entity object that results to creating an entity

        :param use_defaults: if True, the constructor will use the _default_create_kwargs fields. Otherwise this
        class property will be ignored
        :param kwargs: Any additional field values that shall be embedded to the entity or 'id' that reflects the
        entity ID
        """
        super().__init__(use_defaults, **kwargs)
        self._entity_fields['session_key'] = self.entity.session_key.generate(
            EntityPasswordManager.ALL_SYMBOLS,
            ExternalAuthorizationSession.SESSION_KEY_LENGTH
        )
        self.entity.session_key_expiry_date.set(timedelta(minutes=30))
        self._entity_fields['session_key_expiry_date'] = None

    @property
    def last_password(self):
        return self._last_password

    @property
    def default_field_key(self):
        return list(super().default_field_key) + ["session_key", "session_key_expiry_date"]
