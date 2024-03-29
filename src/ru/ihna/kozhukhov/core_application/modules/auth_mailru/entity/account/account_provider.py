from .....entity.providers.model_providers.external_authorization_account_provider import \
    ExternalAuthorizationAccountProvider
from ...models import Account as AccountModel


class AccountProvider(ExternalAuthorizationAccountProvider):
    """
    Provides the information exchange between the account entity and the external data source
    (i.e., the database in this case)
    """

    _entity_model = AccountModel

    _lookup_field = "email"

    _model_fields = ["id", "email", "user"]

    _entity_class = "ru.ihna.kozhukhov.core_application.modules.auth_mailru.entity.Account"
