from core.entity.external_authorization_account import ExternalAuthorizationAccount
from core.entity.entity_fields import EntityField
from authorizations.mailru.entity.account.account_set import AccountSet

from .account_provider import AccountProvider


class Account(ExternalAuthorizationAccount):
    """
    Defines the information about mail.ru account stored on this website
    """

    _entity_set_class = AccountSet

    _entity_provider_list = [AccountProvider()]

    _required_fields = ["email", "user"]

    _intermediate_field_description = {
        "email": EntityField(str, min_length=1, max_length=254,
                             description="Mail.Ru login")
    }
