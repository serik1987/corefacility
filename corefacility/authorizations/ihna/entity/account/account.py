from core.entity.external_authorization_account import ExternalAuthorizationAccount
from core.entity.entity_fields import EntityField

from .account_set import AccountSet
from .account_provider import AccountProvider


class Account(ExternalAuthorizationAccount):
    """
    Defines the record that allows to attach user account in this application to your institution website account
    """

    _entity_set_class = AccountSet

    _entity_provider_list = [AccountProvider()]

    _required_fields = ["email", "user"]

    _intermediate_field_description = {
        "email": EntityField(str, min_length=1, max_length=254,
                             description="IHNA website login")
    }
