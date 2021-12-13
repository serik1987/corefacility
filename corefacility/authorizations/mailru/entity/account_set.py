from core.entity.entity_sets.external_authorization_account_set import ExternalAuthorizationAccountSet


class AccountSet(ExternalAuthorizationAccountSet):
    """
    Connects a particular mail.ru account with different ways to find it both using the external mail.ru website
    and from the local storage
    """

    _entity_name = "Mail.ru account"

    _entity_class = "authorizations.mailru.entity.account.Account"

    _entity_reader_class = None   # TO-DO: define a proper mail.ru account reader
