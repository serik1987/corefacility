from datetime import timedelta

from core.authorizations import StandardAuthorization, AutomaticAuthorization, PasswordRecoveryAuthorization, \
    UnixAuthorization
from core.entity.external_authorization_session import ExternalAuthorizationSession
from core.entity.entity_fields.field_managers.entity_password_manager import EntityPasswordManager

from authorizations.cookie import App as CookieApp
from authorizations.google import App as GoogleApp
from authorizations.mailru import App as MailruApp
from authorizations.ihna import App as IhnaApp

from .entity_set_object import EntitySetObject


class ExternalAuthorizationSessionSetObject(EntitySetObject):

    _entity_class = ExternalAuthorizationSession

    def __init__(self, _entity_list=None):
        if _entity_list is not None:
            self._entities = _entity_list
        else:
            self._entities = []
            for app_class, ntimes in self.data_provider():
                for i in range(ntimes):
                    external_authorization_session = ExternalAuthorizationSession(authorization_module=app_class())
                    external_authorization_session.session_key.generate(EntityPasswordManager.ALL_SYMBOLS, 5)
                    external_authorization_session.session_key_expiry_date.set(timedelta(minutes=30))
                    external_authorization_session.create()
                    self._entities.append(external_authorization_session)

    def data_provider(self):
        return [
            (CookieApp, 2),
            (GoogleApp, 1),
            (MailruApp, 2),
            (IhnaApp, 2),
            (StandardAuthorization, 1),
            (AutomaticAuthorization, 2),
            (PasswordRecoveryAuthorization, 1),
            (UnixAuthorization, 2),
        ]

    def filter_by_authorization_module(self, authorization_module):
        self._entities = list(filter(
            lambda session: session.authorization_module.uuid == authorization_module.uuid,
            self._entities
        ))
