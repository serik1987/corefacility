from ru.ihna.kozhukhov.core_application.test.entity.entity_objects.external_authorization_account_object \
    import ExternalAuthorizationAccountObject
from ..entity import Account


class AccountObject(ExternalAuthorizationAccountObject):
    """
    Facilitates using the account object for testing purpose.
    """

    _entity_class = Account

    _default_create_kwargs = {
        "email": "sergei.kozhukhov@ihna.ru"
    }

    _default_change_kwargs = {
        "email": "sergeykozh@mail.ru"
    }
