from .entity import Entity


class ExternalAuthorizationToken(Entity):
    """
    A base class for all external authorization tokens.

    When the user has been successfully authorized using the external website he sends you the authorization code.
    Your next steps are to access to this particular external website to change the authorization code to the
    authorization token and receive particular information that can attach the authorization token to the user.

    This class allows to store the received authorization tokens either permanently or temporarily
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

    _public_field_description = {}
    """
    Define the following public fields here:
    - the authorization code you need to change to authorization token;
    - all information received from the external website when you send authorization code there;
    - when you want to store the authorization token you can also define the user to which this token is attached
    """

    _required_fields = ["code"]
    """ Contains the list of only such fields that have to be sent to the external server """
