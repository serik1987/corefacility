from .entity import Entity
from .entity_sets.external_authorization_session_set import ExternalAuthorizationSessionSet
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

    _entity_set_class = ExternalAuthorizationSessionSet

    _entity_provider_list = []  # TO-DO: Implement the entity provider list

    _required_fields = ["authorization_module", "session_key", "session_key_expiry_date"]

    _public_field_description = {
        "authorization_module": RelatedEntityField("core.entity.corefacility_module.CorefacilityModule",
                                                   description="Related authorization module"),
        "session_key": ManagedEntityField(EntityPasswordManager,
                                          description="Issued session key"),
        "session_key_expiry_date": ManagedEntityField(ExpiryDateManager,
                                                      description="Session key expiry date")
    }

    @classmethod
    def initialize(cls, module):
        """
        Initializes the external authorization session

        :param module: external authorization module to which the session is related
        :return: session token
        """
        raise NotImplementedError("TO-DO: ExternalAuthorizationSession.initialize")

    @classmethod
    def restore(cls, module, session_token):
        """
        Restores the external authorization session

        :param module: external authorization module to which the session is related
        :param session_token: the session token given during the session initialization
        :return: True if the session is successfully restored, False if session token is invalid, expired or
            has been already used
        """
        raise NotImplementedError("TO-DO: ExternalAuthorizationSession.restore")
