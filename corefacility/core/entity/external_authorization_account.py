from .entity import Entity
from .entity_fields import RelatedEntityField


class ExternalAuthorizationAccount(Entity):
    """
    Declares connection of the user account on the external website with the local authorization account
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

    _required_fields = ["token"]

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
            "token": RelatedEntityField("core.entity.external_authorization_token.ExternalAuthorizationToken",
                                        description="Authorization token"),
            "user": RelatedEntityField("core.entity.user.User",
                                       description="Attached authorization user")
        }
        self._public_field_description.update(self._intermediate_field_description)
        super().__init__(**kwargs)
