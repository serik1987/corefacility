from core.test.entity.entity_objects.external_authorization_account_object import ExternalAuthorizationAccountObject
from authorizations.ihna.entity import Account


class AccountObject(ExternalAuthorizationAccountObject):
    """
    Facilitates creation of test accounts.
    """

    _entity_class = Account

    _default_create_kwargs = {
        "email": "sergei.kozhukhov@ihna.ru"
    }

    _default_change_kwargs = {
        "email": "ivan.ivanov@ihna.ru"
    }
