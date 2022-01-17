from core.test.entity.entity_objects.external_authorization_account_object import ExternalAuthorizationAccountObject
from authorizations.google.entity import Account


class AccountObject(ExternalAuthorizationAccountObject):
    """
    Manages the Google account record for testing purpose.
    """

    _entity_class = Account

    _default_create_kwargs = {
        "email": "serik1987@gmail.com",
    }

    _default_change_kwargs = {
        "email": "kozhukhov@gmail.com",
    }
