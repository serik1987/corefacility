from .entity import Entity
from .fields import EntityField, ReadOnlyField


class ExternalAuthorizationToken(Entity):
    """
    A base class for all external authorization tokens.

    When the user has been successfully authorized using the external website he sends you the authorization code.
    Your next steps are to access to this particular external website to change the authorization code to the
    authorization token and receive particular information that can attach the authorization token to the user.

    This class allows to store the received authorization tokens either permanently or temporarily. Its create()
    method must send an HTTP request to the third-party service in order to exchange the authorization code to
    the authorization token as well as to request all other essential account details. The last step is to use
    the ExternalAuthorizationAccount entity to create particular authentication and attach it to the
    ExternalAuthorizationToken.
    """

    _entity_set_class = None
    """
    If you don't need to store the authorization tokens in the external database, you don't need to touch this field.
    
    In case you store the authorization tokens in the external database you need to give the class name that manages
    several search filters allowing to easily find an appropriate token
    """

    _entity_provider_list = []
    """
    First of all you need to create your first EntityProvider that is responsible for changing your authorization
    code to the authorization code.
    
    Next, if you want to store your authorization tokens on your server you need to develop a second EntityProvider
    that is responsible for such a save.
    
    Both providers (objects itself, not classes) shall be added to this list.
    """

    _initial_field_description = {
        "code": EntityField(str, description="Authorization code"),
        "authentication": ReadOnlyField(description="Related user authentication"),
    }
    """
    Define the following public fields here:
    - the authorization code you need to change to authorization token;
    - all information received from the external website when you send authorization code there;
    - the authentication that shall be attached to this token in case of successful authorization.
    
    The first one and the last one are defined here. Any other fields must be defined in the subclass
    _intermediate_field_description
    """

    _intermediate_field_description = {}

    _required_fields = ["code"]
    """ Contains the list of only such fields that have to be sent to the external server """

    def __init__(self, **kwargs):
        """
        Initializes the entity. The entity can be initialized in the following ways:

        1) Entity(field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by another entities, request views and serializers.
        all values passed to the entity constructor will be validated

        2) Entity(_src=some_external_object, id=value0, field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by entity providers when they try to wrap the object.
        See EntityProvider.wrap_entity for details

        :param kwargs: the fields you want to assign to entity properties
        """
        self._public_field_description = self._initial_field_description.copy()
        self._public_field_description.update(self._intermediate_field_description)
        super().__init__(**kwargs)
