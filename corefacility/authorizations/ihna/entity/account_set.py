from core.entity.entity_sets.external_authorization_account_set import ExternalAuthorizationAccountSet


class AccountSet(ExternalAuthorizationAccountSet):
    """
    Defines the way how to connect the account record with certain ways to look for such account record
    """

    _entity_name = "IHNA RAS account attachment"

    _entity_class = "authorizations.ihna.entity.account.Account"

    _entity_reader_class = None   # TO-DO define a proper entity reader
