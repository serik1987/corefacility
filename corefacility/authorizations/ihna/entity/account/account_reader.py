from core.entity.entity_readers.external_authorization_account_reader import ExternalAuthorizationAccountReader
from core.entity.entity_readers.model_emulators import ModelEmulator

from .account_provider import AccountProvider


class AccountReader(ExternalAuthorizationAccountReader):
    """
    Searches appropriate ihna.ru account in the local database and gives it to the AccountProvider
    """

    _lookup_table_name = "ihna_account"

    _query_debug = False

    _entity_provider = AccountProvider()

    def initialize_query_builder(self):
        super().initialize_query_builder()
        self.items_builder.add_select_expression("ihna_account.email")

    def create_external_object(self, account_id, user_id, user_login, user_name, user_surname, account_email):
        return ModelEmulator(
            id=account_id,
            email=account_email,
            user=ModelEmulator(
                id=user_id,
                login=user_login,
                name=user_name,
                surname=user_surname
            )
        )
