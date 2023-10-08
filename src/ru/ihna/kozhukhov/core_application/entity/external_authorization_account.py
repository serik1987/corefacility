from .entity import Entity
from .fields import RelatedEntityField


class ExternalAuthorizationAccount(Entity):
    """
    The external authorization account is an account that the user has been created on a 3rd part server.

    This entity must be created before the user attempt to log in using the external authorization method.
    The goal of the entity is to provide enough information that unambiguously connect the corefacility account
    to the account on the 3rd part service (usually, this is login name). The entity contains the user entity
    together with the 3rd party account details.

    When the authorization using the 3rd party service is successfull the service itself sends corefacility
    some account details (usually, this is user's login). Then, corefacility finds the entity by such account
    details and looks to a 'user' field of this entity.
    """

    _entity_set_class = None
    """ Fill in this field by another class derived from the ExternalAuthorizationAccountSet """

    _entity_provider_list = []
    """
    1) If the authorization token contains no information needed to recover a certain use you need to develop the
    first entity provider that connects to the first website to exchange the authorization token to some information
    attached to user account on this website
    
    2) Also you need to define another provider that allows to find an appropriate user corresponding to the
    information received from the external website
    """

    _intermediate_field_description = {}
    """
    All public fields on this class are:
    'token' the authorization token that helps us to recover an appropriate user information
    Intermediate fields: any other information attached to the user. Usually you need to access to the server in
    order to exchange the authorization token to the information containing in the intermediate fields
    'user' a final user that have been successfully authorized using this external authorization facility
    
    Define just intermediate fields here
    """

    def __init__(self, **kwargs):
        self._public_field_description = {
            "user": RelatedEntityField("ru.ihna.kozhukhov.core_application.entity.user.User",
                                       description="Attached authorization user")
        }
        self._public_field_description.update(self._intermediate_field_description)
        super().__init__(**kwargs)
