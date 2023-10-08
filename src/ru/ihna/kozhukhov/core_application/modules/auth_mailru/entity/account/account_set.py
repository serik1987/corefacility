from .....entity.entity_sets.external_authorization_account_set import ExternalAuthorizationAccountSet

from .account_reader import AccountReader


class AccountSet(ExternalAuthorizationAccountSet):
    """
    Connects a particular mail.ru account with different ways to find it both using the external mail.ru website
    and from the local storage
    """

    _entity_name = "Mail.ru account"

    _entity_class = "ru.ihna.kozhukhov.core_application.auth_mailru.entity.account.Account"

    _entity_reader_class = AccountReader

    _alias_kwarg = "email"
