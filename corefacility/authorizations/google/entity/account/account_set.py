from core.entity.entity_sets.external_authorization_account_set import ExternalAuthorizationAccountSet

from .account_reader import AccountReader


class AccountSet(ExternalAuthorizationAccountSet):
    """
    Declares basic ways to find a proper Google account
    """

    _entity_name = "Google Account"

    _entity_class = "authorizations.google.entity.account.Account"

    _entity_reader_class = AccountReader

    _alias_kwarg = "email"
