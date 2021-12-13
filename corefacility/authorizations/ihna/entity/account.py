from core.entity.external_authorization_account import ExternalAuthorizationAccount
from core.entity.entity_fields import EntityField
from .account_set import AccountSet


class Account(ExternalAuthorizationAccount):
    """
    Defines the record that allows to attach user account in this application to your institution website account
    """

    _entity_set_class = AccountSet

    _entity_provider_list = None   # TO-DO: Define all entity providers

    _intermediate_field_description = {
        "email": EntityField(str, min_length=1, max_length=254,
                             default="IHNA website login")
    }
