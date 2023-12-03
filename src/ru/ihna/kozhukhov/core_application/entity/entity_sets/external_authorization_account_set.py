from .entity_set import EntitySet


class ExternalAuthorizationAccountSet(EntitySet):
    """
    Declares all facilities to find an appropriate external authorization account.

    The basic purpose of this class is to connect some ExternalAuthorizationAccount and
    proper account reader
    """

    _entity_name = None
    """ Fill in this field by a short string defining the meaning of this class """

    _entity_class = None
    """
    Fill in this field by the full class derived from the
    ru.ihna.kozhukhov.core_application.entity.external_authorization_account.ExternalAuthorizationAccount
    
    This field must contain string representation of this class
    """

    _entity_reader_class = None
    """ Fill in this field by another class responsible for finding appropriate account using the token """

    _entity_filter_list = {
        "user": ["ru.ihna.kozhukhov.core_application.entity.user.User", None]
    }
