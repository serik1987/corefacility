from core.entity.entity_providers.model_providers.external_authorization_account_provider import \
    ExternalAuthorizationAccountProvider
from core.entity.entity_providers.model_providers.user_provider import UserProvider
from authorizations.google.models import Account as AccountModel


class AccountProvider(ExternalAuthorizationAccountProvider):
    """
    Exchanges information between the google's Account entity and the database
    """

    _entity_model = AccountModel

    _lookup_field = "email"

    _model_fields = ["email", "user"]

    _entity_class = "authorizations.google.entity.Account"
