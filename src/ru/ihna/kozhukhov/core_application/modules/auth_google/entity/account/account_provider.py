from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.external_authorization_account_provider \
    import ExternalAuthorizationAccountProvider
from ...models import Account as AccountModel


class AccountProvider(ExternalAuthorizationAccountProvider):
    """
    Exchanges information between the google's Account entity and the database
    """

    _entity_model = AccountModel

    _lookup_field = "email"

    _model_fields = ["email", "user"]

    _entity_class = "ru.ihna.kozhukhov.core_application.modules.auth_google.entity.Account"
