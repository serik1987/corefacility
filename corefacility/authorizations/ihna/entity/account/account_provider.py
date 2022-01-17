from core.entity.entity_providers.model_providers.external_authorization_account_provider import \
    ExternalAuthorizationAccountProvider
from authorizations.ihna.models import Account as AccountModel


class AccountProvider(ExternalAuthorizationAccountProvider):
    """
    The class is responsible for the data exchange between the Account entity and the database.
    """

    _entity_model = AccountModel

    _lookup_field = "email"

    _model_fields = ["email", "user"]

    _entity_class = "authorizations.ihna.entity.Account"
