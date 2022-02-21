from base64 import b64encode, b64decode
from datetime import timedelta

from .entity import Entity
from .entity_exceptions import EntityNotFoundException
from .entity_sets.external_authorization_session_set import ExternalAuthorizationSessionSet
from .entity_providers.model_providers.external_authorization_session_provider import \
    ExternalAuthorizationSessionProvider
from .entity_fields import RelatedEntityField, ManagedEntityField, EntityPasswordManager, ExpiryDateManager


class ExternalAuthorizationSession(Entity):
    """
    An external authorization session.

    When the use try to authorize through external source he sends request to this application that results to
    creating external authorization session and issuing session token. Next, the user is redirected to the
    outside website.

    After the user finish login at the outside website the website itself must redirect the user to this web
    application and give him an authorization token issued earlier. This entity will restore the authorization
    session using this token. After successful restoration of the session the external authorization token
    destroys.

    Every external authorization token has very short live time that shall be defined by the authorization module
    itself
    """

    SESSION_KEY_LENGTH = 10

    _entity_set_class = ExternalAuthorizationSessionSet

    _entity_provider_list = [ExternalAuthorizationSessionProvider()]

    _required_fields = ["authorization_module", "session_key", "session_key_expiry_date"]

    _public_field_description = {
        "authorization_module": RelatedEntityField("core.entity.entry_points.authorizations.AuthorizationModule",
                                                   description="Related authorization module"),
        "session_key": ManagedEntityField(EntityPasswordManager,
                                          description="Issued session key"),
        "session_key_expiry_date": ManagedEntityField(ExpiryDateManager,
                                                      description="Session key expiry date")
    }

    @classmethod
    def initialize(cls, module, expiry_term: timedelta):
        """
        Initializes the external authorization session

        :param module: external authorization module to which the session is related
        :param expiry_term: the session key expiry term (an instance of datetime.timedelta
        :return: session token
        """
        session = cls(authorization_module=module)
        session_key = session.session_key.generate(EntityPasswordManager.ALL_SYMBOLS, cls.SESSION_KEY_LENGTH)
        session.session_key_expiry_date.set(expiry_term)
        session.create()
        session_info = "%s:%s" % (session.id, session_key)
        session_token = b64encode(session_info.encode("utf-8")).decode("utf-8")
        return session_token

    @classmethod
    def restore(cls, module, session_token):
        """
        Restores the external authorization session

        :param module: external authorization module to which the session is related
        :param session_token: the session token given during the session initialization
        :return: True if the session is successfully restored, False if session token is invalid, expired or
            has been already used
        """
        try:
            session_info = b64decode(session_token.encode("utf-8")).decode("utf-8")
            session_id, session_password = session_info.split(":", maxsplit=1)
        except ValueError:
            raise EntityNotFoundException()
        session_set = cls.get_entity_set_class()()
        session = session_set.get(int(session_id))
        if session.authorization_module.get_alias() != module.get_alias():
            raise EntityNotFoundException()
        if session.session_key_expiry_date.is_expired():
            raise EntityNotFoundException()
        if not session.session_key.check(session_password):
            raise EntityNotFoundException()
        session.delete()
